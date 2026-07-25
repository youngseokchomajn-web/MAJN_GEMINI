/**
 * Three.js 3D Deformed Box Shell Viewer & 2D Interactive Exciter positioning canvas renderer.
 * Features Enclosed Box, Internal Exciters mounted under the top plate, and Clean No-Grid View.
 */

class WoodHousingFEMVisualizer {
  constructor(container3DId, canvas2DId, femEngine, dispSolver = null) {
    this.container3D = document.getElementById(container3DId);
    this.canvas2D = document.getElementById(canvas2DId);
    this.ctx2D = this.canvas2D ? this.canvas2D.getContext('2d') : null;
    this.engine = femEngine;
    this.dispSolver = dispSolver;

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.mesh3D = null;
    this.sideWallMeshes = [];
    this.boltPins3D = [];
    this.exciterMeshes3D = [];

    this.draggedExciterId = null;
    this.draggedBaby = false;
    this.draggedSensor = false;

    this.init3D();
    this.init2DEvents();
    this.render();
  }

  init3D() {
    if (!this.container3D || typeof THREE === 'undefined') return;

    const width = this.container3D.clientWidth || 600;
    const height = this.container3D.clientHeight || 350;

    this.scene = new THREE.Scene();
    // Bright Clean White Studio Background
    this.scene.background = new THREE.Color(0xf8fafc);

    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    this.camera.position.set(0, -1.2, 0.9);
    this.camera.lookAt(0, 0, 0);

    const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    this.scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x0284c7, 0.8);
    dirLight1.position.set(2, 3, 4);
    this.scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xffedd5, 0.9);
    dirLight2.position.set(-2, -2, 3);
    this.scene.add(dirLight2);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container3D.appendChild(this.renderer.domElement);

    if (typeof THREE.OrbitControls !== 'undefined') {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.maxPolarAngle = Math.PI / 2 + 0.2;
    }

    // Grid helper completely removed for clean 3D view

    this.rebuild3DMesh();
  }

  setCameraPreset(viewType) {
    if (!this.camera) return;
    const centerZ = -((this.engine.depth || 0.06) / 2.0);
    if (this.controls) {
      this.controls.target.set(0, 0, centerZ);
    }
    if (viewType === 'front') {
      this.camera.position.set(0, -1.8, centerZ);
    } else if (viewType === 'top') {
      // Offset Y slightly to (0, 0.001, 1.8) to prevent OrbitControls Gimbal Lock
      this.camera.position.set(0, 0.001, 1.8);
      this.camera.up.set(0, 1, 0);
    } else {
      // Isometric view
      this.camera.position.set(0, -1.2, 0.9 + centerZ);
      this.camera.up.set(0, 0, 1);
    }
    this.camera.lookAt(0, 0, centerZ);
    if (this.controls) this.controls.update();
  }

  rebuild3DMesh() {
    if (!this.scene || typeof THREE === 'undefined') return;
    const centerZ = -((this.engine.depth || 0.06) / 2.0);
    if (this.controls) {
      this.controls.target.set(0, 0, centerZ);
      this.controls.update();
    }

    if (this.mesh3D) {
      this.scene.remove(this.mesh3D);
      this.mesh3D.geometry.dispose();
      this.mesh3D.material.dispose();
    }

    this.sideWallMeshes.forEach(m => this.scene.remove(m));
    this.sideWallMeshes = [];

    this.boltPins3D.forEach(pin => this.scene.remove(pin));
    this.boltPins3D = [];

    this.exciterMeshes3D.forEach(ex => this.scene.remove(ex));
    this.exciterMeshes3D = [];

    // Top Plate 3D Mesh (Birch Wood with Slight Translucency for Inner Exciter View)
    const geom = new THREE.PlaneGeometry(this.engine.width, this.engine.height, this.engine.nx, this.engine.ny);
    const count = geom.attributes.position.count;
    const colors = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      colors[i * 3 + 0] = 0.96; colors[i * 3 + 1] = 0.81; colors[i * 3 + 2] = 0.66;
    }
    geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const mat = new THREE.MeshStandardMaterial({
      vertexColors: true,
      wireframe: false,
      side: THREE.DoubleSide,
      roughness: 0.45,
      metalness: 0.05,
      transparent: true,
      opacity: 0.88 // Slightly translucent to reveal inner exciters
    });

    this.mesh3D = new THREE.Mesh(geom, mat);
    this.scene.add(this.mesh3D);

    // 4 Side Walls (Enclosed Box Shell: Birch Plywood Edge Tone #c58f59)
    const pW = this.engine.width;
    const pH = this.engine.height;
    const pD = this.engine.depth || 0.06;
    const sideMat = new THREE.MeshStandardMaterial({ color: 0xc58f59, roughness: 0.55, side: THREE.DoubleSide });

    // Front / Back Walls
    const fbGeom = new THREE.PlaneGeometry(pW, pD);
    const frontWall = new THREE.Mesh(fbGeom, sideMat);
    frontWall.position.set(0, -pH / 2, -pD / 2);
    frontWall.rotation.x = Math.PI / 2;
    this.scene.add(frontWall);
    this.sideWallMeshes.push(frontWall);

    const backWall = new THREE.Mesh(fbGeom, sideMat);
    backWall.position.set(0, pH / 2, -pD / 2);
    backWall.rotation.x = Math.PI / 2;
    this.scene.add(backWall);
    this.sideWallMeshes.push(backWall);

    // Left / Right Walls
    const lrGeom = new THREE.PlaneGeometry(pH, pD);
    const leftWall = new THREE.Mesh(lrGeom, sideMat);
    leftWall.position.set(-pW / 2, 0, -pD / 2);
    leftWall.rotation.y = Math.PI / 2;
    leftWall.rotation.z = Math.PI / 2;
    this.scene.add(leftWall);
    this.sideWallMeshes.push(leftWall);

    const rightWall = new THREE.Mesh(lrGeom, sideMat);
    rightWall.position.set(pW / 2, 0, -pD / 2);
    rightWall.rotation.y = Math.PI / 2;
    rightWall.rotation.z = Math.PI / 2;
    this.scene.add(rightWall);
    this.sideWallMeshes.push(rightWall);

    // 3D Bolted Joint Pins (8 Brass Metal Pins)
    for (const bolt of this.engine.bolts) {
      const pinGeom = new THREE.CylinderGeometry(0.008, 0.008, 0.035, 16);
      const pinMat = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.85, roughness: 0.2 });
      const pinMesh = new THREE.Mesh(pinGeom, pinMat);

      let px = (bolt.xNorm - 0.5) * this.engine.width;
      let py = (bolt.yNorm - 0.5) * this.engine.height;
      pinMesh.position.set(px, py, 0.01);
      pinMesh.rotation.x = Math.PI / 2;
      this.scene.add(pinMesh);
      this.boltPins3D.push(pinMesh);
    }

    // 3D Exciter Units - Mounted INSIDE Under the Top Plate (Z = -0.010)
    for (const exciter of this.engine.exciters) {
      const exGeom = new THREE.CylinderGeometry(0.022, 0.022, 0.014, 24);
      const exMat = new THREE.MeshStandardMaterial({ color: 0xec4899, metalness: 0.8, roughness: 0.2 });
      const exMesh = new THREE.Mesh(exGeom, exMat);

      let exX = (exciter.x - 0.5) * this.engine.width;
      let exY = (exciter.y - 0.5) * this.engine.height;
      // Position Z = -0.010 (Mounted under top plate inside box)
      exMesh.position.set(exX, exY, -0.010);
      exMesh.rotation.x = Math.PI / 2;
      this.scene.add(exMesh);
      this.exciterMeshes3D.push(exMesh);
    }
  }

  update3DMesh(time = 0) {
    if (!this.mesh3D) return;

    const pos = this.mesh3D.geometry.attributes.position;
    const col = this.mesh3D.geometry.attributes.color;

    const scaleDeflect = 30.0;
    const maxSt = Math.max(0.5, this.engine.maxStress);

    // Update 3D Bolt Pins Position continuously
    for (let bIdx = 0; bIdx < this.engine.bolts.length; bIdx++) {
      if (this.boltPins3D[bIdx]) {
        const bolt = this.engine.bolts[bIdx];
        let px = (bolt.xNorm - 0.5) * this.engine.width;
        let py = (bolt.yNorm - 0.5) * this.engine.height;
        this.boltPins3D[bIdx].position.set(px, py, 0.01);
      }
    }

    // Update 3D Exciter Meshes Position continuously
    for (let exIdx = 0; exIdx < this.engine.exciters.length; exIdx++) {
      if (this.exciterMeshes3D[exIdx]) {
        const exciter = this.engine.exciters[exIdx];
        let exX = (exciter.x - 0.5) * this.engine.width;
        let exY = (exciter.y - 0.5) * this.engine.height;
        this.exciterMeshes3D[exIdx].position.set(exX, exY, -0.010);
      }
    }

    for (let idx = 0; idx < pos.count; idx++) {
      if (idx < this.engine.nodes.length) {
        let w = this.engine.deflections[idx] || 0;
        let sig = this.engine.stresses[idx] || 0;

        // Mode Shape 3D Deformation Override
        if (this.activeModeIdx && this.activeModeIdx > 0) {
          const node = this.engine.nodes[idx];
          const m = this.activeModeIdx === 1 ? 1 : (this.activeModeIdx === 2 ? 2 : (this.activeModeIdx === 3 ? 1 : 2));
          const n = this.activeModeIdx === 1 ? 1 : (this.activeModeIdx === 2 ? 1 : (this.activeModeIdx === 3 ? 2 : 2));
          const modeAmp = Math.sin(m * Math.PI * node.xNorm) * Math.sin(n * Math.PI * node.yNorm);
          const omegaM = 2 * Math.PI * (this.engine.naturalFrequencies ? this.engine.naturalFrequencies[this.activeModeIdx - 1] : 48.5);
          w = modeAmp * 0.003 * Math.sin(omegaM * (time / 1000.0));
        }

        pos.setZ(idx, -w * scaleDeflect);

        if (this.renderMode === 'displacement') {
          // 1. Displacement Color Contour (0mm Blue -> Green -> Red Max Deflection)
          let wRatio = Math.min(1.0, Math.abs(w) / (Math.max(0.0001, this.engine.maxDeflection / 1000.0) * 1.2));
          let hue = (1.0 - wRatio) * 240; // 240 (Blue) -> 0 (Red)
          let rgb = hslToRgb(hue / 360, 0.85, 0.50);
          col.setXYZ(idx, rgb[0], rgb[1], rgb[2]);
        } else if (this.renderMode === 'thermal' && typeof TopPlateDisplacementSolver !== 'undefined') {
          // 2. Thermal Heatmap Contour (25.0°C Blue -> 41.7°C Red)
          const node = this.engine.nodes[idx];
          let dT = 0;
          const volRatio = (this.engine.exciterVolumePct !== undefined ? this.engine.exciterVolumePct : 40) / 100.0;
          for (const ex of this.engine.exciters) {
            const dSq = Math.pow(node.xNorm - ex.x, 2) + Math.pow(node.yNorm - ex.y, 2);
            dT += 16.7 * (volRatio / 0.40) * Math.exp(-dSq * 20.0);
          }
          let tRatio = Math.min(1.0, dT / 16.7);
          col.setXYZ(idx, tRatio, 0.2 * (1 - tRatio), 1 - tRatio);
        } else if (this.renderMode === 'wood') {
          // 3. Natural Birch Wood Texture Tone
          col.setXYZ(idx, 0.96, 0.81, 0.66);
        } else {
          // 4. Von Mises Stress Heatmap Contour (Default)
          let ratio = Math.min(1.0, sig / (maxSt * 1.1));
          let r = 0.96;
          let g = 0.81;
          let b = 0.66;
          if (ratio > 0.05) {
            r = 0.2 + 0.8 * ratio;
            g = 0.8 * (1.0 - ratio);
            b = 0.2;
          }
          col.setXYZ(idx, r, g, b);
        }
      }
    }

    pos.needsUpdate = true;
    col.needsUpdate = true;
  }

  init2DEvents() {
    if (!this.canvas2D) return;

    this.canvas2D.addEventListener('mousedown', (e) => {
      const rect = this.canvas2D.getBoundingClientRect();
      const clickX = (e.clientX - rect.left) / rect.width;
      const clickY = (e.clientY - rect.top) / rect.height;

      // 1. Check Exciter Drag
      for (const exciter of this.engine.exciters) {
        const dist = Math.hypot(exciter.x - clickX, exciter.y - clickY);
        if (dist < 0.06) {
          this.draggedExciterId = exciter.id;
          return;
        }
      }

      // 2. Check Bolt Drag (Increased hit-test radius for smooth dragging)
      for (let bIdx = 0; bIdx < this.engine.bolts.length; bIdx++) {
        const bolt = this.engine.bolts[bIdx];
        const distB = Math.hypot(bolt.xNorm - clickX, bolt.yNorm - clickY);
        if (distB < 0.09) {
          this.draggedBoltIdx = bIdx;
          return;
        }
      }

      // 3. Check LSM6DSOX Sensor Drag
      if (this.dispSolver) {
        const sPos = this.dispSolver.sensorPos;
        const distS = Math.hypot(sPos.xNorm - clickX, sPos.yNorm - clickY);
        if (distS < 0.07) {
          this.draggedSensor = true;
          return;
        }
      }

      // 4. Check Baby Payload Drag
      const distBaby = Math.hypot(this.engine.babyPosX - clickX, this.engine.babyPosY - clickY);
      if (distBaby < 0.08) {
        this.draggedBaby = true;
        return;
      }
    });

    this.canvas2D.addEventListener('mousemove', (e) => {
      const rect = this.canvas2D.getBoundingClientRect();
      const normX = (e.clientX - rect.left) / rect.width;
      const normY = (e.clientY - rect.top) / rect.height;

      if (this.draggedExciterId !== null) {
        this.engine.updateExciterPos(this.draggedExciterId, normX, normY);
        this.rebuild3DMesh();
      } else if (this.draggedBoltIdx !== undefined && this.draggedBoltIdx !== null) {
        // Snap-to-Wall Perimeter Trajectory: Restrict bolts strictly onto 4 Side Wall Frame Lines
        let x = Math.max(0.06, Math.min(0.94, normX));
        let y = Math.max(0.06, Math.min(0.94, normY));

        let distLeft = Math.abs(x - 0.06);
        let distRight = Math.abs(x - 0.94);
        let distFront = Math.abs(y - 0.06);
        let distBack = Math.abs(y - 0.94);

        let minDist = Math.min(distLeft, distRight, distFront, distBack);

        if (minDist === distLeft) x = 0.06;
        else if (minDist === distRight) x = 0.94;
        else if (minDist === distFront) y = 0.06;
        else if (minDist === distBack) y = 0.94;

        this.engine.bolts[this.draggedBoltIdx].xNorm = x;
        this.engine.bolts[this.draggedBoltIdx].yNorm = y;
        this.engine.generateMesh();
        this.engine.solve();
        this.rebuild3DMesh();
      } else if (this.draggedSensor && this.dispSolver) {
        this.dispSolver.setSensorPosition(normX, normY);
        if (typeof initFRFChart === 'function') initFRFChart();
      } else if (this.draggedBaby) {
        this.engine.babyPosX = Math.max(0.05, Math.min(0.95, normX));
        this.engine.babyPosY = Math.max(0.05, Math.min(0.95, normY));
        this.engine.solve();
      }
    });

    window.addEventListener('mouseup', () => {
      this.draggedExciterId = null;
      this.draggedBoltIdx = null;
      this.draggedBaby = false;
      this.draggedSensor = false;
    });
  }

  render2D() {
    if (!this.ctx2D) return;

    const w = this.canvas2D.width = this.canvas2D.clientWidth;
    const h = this.canvas2D.height = this.canvas2D.clientHeight;

    this.ctx2D.clearRect(0, 0, w, h);
    this.ctx2D.fillStyle = '#f8fafc';
    this.ctx2D.fillRect(0, 0, w, h);

    const margin = 20;
    const hw = w - margin * 2;
    const hh = h - margin * 2;

    this.ctx2D.lineWidth = 2.5;
    this.ctx2D.strokeStyle = '#0284c7';
    this.ctx2D.fillStyle = 'rgba(245, 208, 169, 0.4)';

    this.ctx2D.beginPath();
    this.ctx2D.rect(margin, margin, hw, hh);
    this.ctx2D.fill();
    this.ctx2D.stroke();

    for (const node of this.engine.nodes) {
      if (!node.inside) continue;
      const px = margin + node.xNorm * hw;
      const py = margin + node.yNorm * hh;

      const idx = node.id;
      const sig = this.engine.stresses[idx] || 0;
      const ratio = Math.min(1.0, sig / (Math.max(0.5, this.engine.maxStress) * 1.1));

      let hue = 35 - ratio * 35;
      let light = 70 - ratio * 20;
      this.ctx2D.fillStyle = `hsl(${hue}, 85%, ${light}%)`;
      this.ctx2D.beginPath();
      this.ctx2D.arc(px, py, 3, 0, Math.PI * 2);
      this.ctx2D.fill();
    }

    for (const bolt of this.engine.bolts) {
      const bx = margin + bolt.xNorm * hw;
      const by = margin + bolt.yNorm * hh;

      this.ctx2D.fillStyle = '#d97706';
      this.ctx2D.strokeStyle = '#fff';
      this.ctx2D.lineWidth = 1.5;
      this.ctx2D.beginPath();
      this.ctx2D.arc(bx, by, 6, 0, Math.PI * 2);
      this.ctx2D.fill();
      this.ctx2D.stroke();
    }

    const bx = margin + this.engine.babyPosX * hw;
    const by = margin + this.engine.babyPosY * hh;

    this.ctx2D.fillStyle = '#fde047';
    this.ctx2D.strokeStyle = '#eab308';
    this.ctx2D.beginPath();
    this.ctx2D.arc(bx, by, 14, 0, Math.PI * 2);
    this.ctx2D.fill();
    this.ctx2D.stroke();
    this.ctx2D.fillStyle = '#000';
    this.ctx2D.font = 'bold 11px sans-serif';
    this.ctx2D.fillText('Baby', bx - 12, by + 4);

    for (let idx = 0; idx < this.engine.exciters.length; idx++) {
      const exciter = this.engine.exciters[idx];
      const ex = margin + exciter.x * hw;
      const ey = margin + exciter.y * hh;

      this.ctx2D.strokeStyle = 'rgba(236, 72, 153, 0.8)';
      this.ctx2D.lineWidth = 2;
      this.ctx2D.beginPath();
      this.ctx2D.arc(ex, ey, 14 + Math.sin(Date.now() / 150 + idx) * 3, 0, Math.PI * 2);
      this.ctx2D.stroke();

      this.ctx2D.fillStyle = '#ec4899';
      this.ctx2D.beginPath();
      this.ctx2D.arc(ex, ey, 9, 0, Math.PI * 2);
      this.ctx2D.fill();

      this.ctx2D.fillStyle = '#fff';
      this.ctx2D.font = 'bold 10px sans-serif';
      this.ctx2D.fillText(`E${idx+1}`, ex - 6, ey + 3);
    }

    // Render LSM6DSOX Virtual Sensor Pin (📍 Purple Pin Marker)
    if (this.dispSolver) {
      const sx = margin + this.dispSolver.sensorPos.xNorm * hw;
      const sy = margin + this.dispSolver.sensorPos.yNorm * hh;

      this.ctx2D.fillStyle = '#a855f7';
      this.ctx2D.strokeStyle = '#ffffff';
      this.ctx2D.lineWidth = 2;
      this.ctx2D.beginPath();
      this.ctx2D.arc(sx, sy, 11, 0, Math.PI * 2);
      this.ctx2D.fill();
      this.ctx2D.stroke();

      this.ctx2D.fillStyle = '#ffffff';
      this.ctx2D.font = 'bold 10px sans-serif';
      this.ctx2D.fillText('S1', sx - 6, sy + 3);
    }
  }

  render(time = 0) {
    this.engine.solve(time / 1000.0);
    this.update3DMesh(time / 1000.0);
    if (this.controls) {
      this.controls.update();
    }
    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
    this.render2D();
    if (typeof updateMetricsUI === 'function') {
      updateMetricsUI();
    }
    requestAnimationFrame((t) => this.render(t));
  }
}

function hslToRgb(h, s, l) {
  let r, g, b;
  if (s === 0) {
    r = g = b = l;
  } else {
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r = hue2rgb(p, q, h + 1/3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1/3);
  }
  return [r, g, b];
}

function hue2rgb(p, q, t) {
  if (t < 0) t += 1;
  if (t > 1) t -= 1;
  if (t < 1/6) return p + (q - p) * 6 * t;
  if (t < 1/2) return q;
  if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
  return p;
}

if (typeof window !== 'undefined') {
  window.WoodHousingFEMVisualizer = WoodHousingFEMVisualizer;
}
