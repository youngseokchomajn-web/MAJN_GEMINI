/**
 * Three.js 3D Deformed Box Shell Viewer & 2D Interactive Exciter positioning canvas renderer.
 * Features 3D Box Enclosure Mesh (Top Plate & 4 Side Walls) and Bolted Joint Pins.
 */

class WoodHousingFEMVisualizer {
  constructor(container3DId, canvas2DId, femEngine) {
    this.container3D = document.getElementById(container3DId);
    this.canvas2D = document.getElementById(canvas2DId);
    this.ctx2D = this.canvas2D ? this.canvas2D.getContext('2d') : null;
    this.engine = femEngine;

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.mesh3D = null;
    this.sideWallMeshes = [];
    this.boltPins3D = [];

    this.draggedExciterId = null;
    this.draggedBaby = false;

    this.init3D();
    this.init2DEvents();
    this.render();
  }

  init3D() {
    if (!this.container3D || typeof THREE === 'undefined') return;

    const width = this.container3D.clientWidth || 600;
    const height = this.container3D.clientHeight || 350;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x060913);

    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    this.camera.position.set(0, -1.3, 1.0);
    this.camera.lookAt(0, 0, 0);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x38bdf8, 1.3);
    dirLight.position.set(2, 2, 4);
    this.scene.add(dirLight);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container3D.appendChild(this.renderer.domElement);

    if (typeof THREE.OrbitControls !== 'undefined') {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
    }

    const grid = new THREE.GridHelper(2.5, 25, 0x1e293b, 0x0f172a);
    grid.rotation.x = Math.PI / 2;
    grid.position.z = -0.12;
    this.scene.add(grid);

    this.rebuild3DMesh();
  }

  rebuild3DMesh() {
    if (!this.scene || typeof THREE === 'undefined') return;

    if (this.mesh3D) {
      this.scene.remove(this.mesh3D);
      this.mesh3D.geometry.dispose();
      this.mesh3D.material.dispose();
    }

    this.sideWallMeshes.forEach(m => this.scene.remove(m));
    this.sideWallMeshes = [];

    this.boltPins3D.forEach(pin => this.scene.remove(pin));
    this.boltPins3D = [];

    // Top Plate 3D Mesh with Vertex Colors
    const geom = new THREE.PlaneGeometry(this.engine.width, this.engine.height, this.engine.nx, this.engine.ny);
    const count = geom.attributes.position.count;
    const colors = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      colors[i * 3 + 0] = 0.2; colors[i * 3 + 1] = 0.6; colors[i * 3 + 2] = 1.0;
    }
    geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const mat = new THREE.MeshStandardMaterial({
      vertexColors: true,
      wireframe: false,
      side: THREE.DoubleSide,
      roughness: 0.3,
      metalness: 0.2
    });

    this.mesh3D = new THREE.Mesh(geom, mat);
    this.scene.add(this.mesh3D);

    // 4 Side Walls to complete 3D Box Enclosure Shape
    const pW = this.engine.width;
    const pH = this.engine.height;
    const pD = this.engine.depth || 0.06;
    const sideMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.7, side: THREE.DoubleSide });

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

    // 3D Bolted Pins (8 Points)
    for (const bolt of this.engine.bolts) {
      const pinGeom = new THREE.CylinderGeometry(0.010, 0.010, 0.04, 16);
      const pinMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.8, roughness: 0.2 });
      const pinMesh = new THREE.Mesh(pinGeom, pinMat);

      let px = (bolt.xNorm - 0.5) * this.engine.width;
      let py = (bolt.yNorm - 0.5) * this.engine.height;
      pinMesh.position.set(px, py, 0.01);
      pinMesh.rotation.x = Math.PI / 2;
      this.scene.add(pinMesh);
      this.boltPins3D.push(pinMesh);
    }
  }

  update3DMesh(time = 0) {
    if (!this.mesh3D) return;

    const pos = this.mesh3D.geometry.attributes.position;
    const col = this.mesh3D.geometry.attributes.color;

    const scaleDeflect = 60.0;
    const maxSt = Math.max(1.0, this.engine.maxStress);

    for (let idx = 0; idx < pos.count; idx++) {
      if (idx < this.engine.nodes.length) {
        let w = this.engine.deflections[idx] || 0;
        let sig = this.engine.stresses[idx] || 0;

        pos.setZ(idx, -w * scaleDeflect);

        let ratio = Math.min(1.0, sig / (maxSt * 1.1));
        let r = Math.min(1.0, ratio * 2.2);
        let g = ratio < 0.5 ? ratio * 2.0 : 2.0 - ratio * 2.0;
        let b = Math.max(0, 1.0 - ratio * 2.2);

        col.setXYZ(idx, r, g, b);
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

      for (const exciter of this.engine.exciters) {
        const dist = Math.hypot(exciter.x - clickX, exciter.y - clickY);
        if (dist < 0.06) {
          this.draggedExciterId = exciter.id;
          return;
        }
      }

      const distBaby = Math.hypot(this.engine.babyPosX - clickX, this.engine.babyPosY - clickY);
      if (distBaby < 0.08) {
        this.draggedBaby = true;
        return;
      }
    });

    this.canvas2D.addEventListener('mousemove', (e) => {
      if (this.draggedExciterId !== null) {
        const rect = this.canvas2D.getBoundingClientRect();
        const normX = (e.clientX - rect.left) / rect.width;
        const normY = (e.clientY - rect.top) / rect.height;
        this.engine.updateExciterPos(this.draggedExciterId, normX, normY);
      } else if (this.draggedBaby) {
        const rect = this.canvas2D.getBoundingClientRect();
        this.engine.babyPosX = Math.max(0.1, Math.min(0.9, (e.clientX - rect.left) / rect.width));
        this.engine.babyPosY = Math.max(0.1, Math.min(0.9, (e.clientY - rect.top) / rect.height));
        this.engine.solve();
      }
    });

    window.addEventListener('mouseup', () => {
      this.draggedExciterId = null;
      this.draggedBaby = false;
    });
  }

  render2D() {
    if (!this.ctx2D) return;

    const w = this.canvas2D.width = this.canvas2D.clientWidth;
    const h = this.canvas2D.height = this.canvas2D.clientHeight;

    this.ctx2D.clearRect(0, 0, w, h);
    this.ctx2D.fillStyle = '#060913';
    this.ctx2D.fillRect(0, 0, w, h);

    const margin = 20;
    const hw = w - margin * 2;
    const hh = h - margin * 2;

    this.ctx2D.lineWidth = 3;
    this.ctx2D.strokeStyle = '#38bdf8';
    this.ctx2D.fillStyle = 'rgba(56, 189, 248, 0.05)';

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
      const ratio = Math.min(1.0, sig / (Math.max(1, this.engine.maxStress) * 1.1));

      this.ctx2D.fillStyle = `hsl(${220 - ratio * 220}, 90%, 55%)`;
      this.ctx2D.beginPath();
      this.ctx2D.arc(px, py, 3, 0, Math.PI * 2);
      this.ctx2D.fill();
    }

    for (const bolt of this.engine.bolts) {
      const bx = margin + bolt.xNorm * hw;
      const by = margin + bolt.yNorm * hh;

      this.ctx2D.fillStyle = '#f59e0b';
      this.ctx2D.strokeStyle = '#fff';
      this.ctx2D.lineWidth = 1.5;
      this.ctx2D.beginPath();
      this.ctx2D.arc(bx, by, 7, 0, Math.PI * 2);
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

      this.ctx2D.strokeStyle = 'rgba(236, 72, 153, 0.6)';
      this.ctx2D.lineWidth = 2;
      this.ctx2D.beginPath();
      this.ctx2D.arc(ex, ey, 16 + Math.sin(Date.now() / 150 + idx) * 4, 0, Math.PI * 2);
      this.ctx2D.stroke();

      this.ctx2D.fillStyle = '#ec4899';
      this.ctx2D.beginPath();
      this.ctx2D.arc(ex, ey, 10, 0, Math.PI * 2);
      this.ctx2D.fill();

      this.ctx2D.fillStyle = '#fff';
      this.ctx2D.font = 'bold 10px sans-serif';
      this.ctx2D.fillText(`E${idx+1}`, ex - 6, ey + 3);
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
    requestAnimationFrame((t) => this.render(t));
  }
}

if (typeof window !== 'undefined') {
  window.WoodHousingFEMVisualizer = WoodHousingFEMVisualizer;
}
