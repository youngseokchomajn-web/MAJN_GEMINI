/**
 * MAJN Smart Bassinet - 3D Box Enclosure CAD & 6-Way Exploded View Engine
 * Renders Top Plate (4mm), Bottom Plate (4mm), 4 Side Walls (60mm depth), Corner L-Brackets,
 * EVA Foam Gasket, 4x TEAX14C02 Exciters, ESP32 Control Box PCB, and M3 Bolt Assemblies.
 */

class CADAssemblyViewer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.scene = null;
    this.camera = null;
    this.renderer = null;

    // Exploded View factor (0.0 = assembled box, 1.0 = 6-way expanded)
    this.explodedFactor = 0.0;

    // Component Layer Groups for 6-Directional Explosion Offsets
    this.layers = {
      washableSleeve: { group: new THREE.Group(), baseZ: 0.048, name: '원터치 세탁 방수 슬리브 커버 (Washable Sleeve)', cost: '$2.5 (소모품)', spec: 'Waterproof Fabric, 10s Snap-on' },
      topPlate: { group: new THREE.Group(), baseZ: 0.032, name: '상판 자작합판 (4mm Birch Plywood)', cost: '$1.2', spec: '720x390x4mm Top Panel' },
      evaGasket: { group: new THREE.Group(), baseZ: 0.026, name: 'EVA 폼 완충 차음 가스켓', cost: '$0.6', spec: 'Density 45kg/m³, High Damping' },
      exciters: { group: new THREE.Group(), baseZ: 0.010, name: 'TEAX14C02-8 익사이터 (4개 유닛)', cost: '$20.0 (4개)', spec: '8Ω 10W Transducers, 3M VHB Tape' },
      controlBox: { group: new THREE.Group(), baseZ: -0.005, name: '컨트롤박스 하우징 & PCB', cost: '$13.0 (PCB+케이스)', spec: 'ESP32-S3 + TAS5805M + MP3426 12.12V' },
      
      // 4 Side Walls for 3D Box Enclosure
      frontWall: { group: new THREE.Group(), baseY: -0.195, name: '전면 측판 자작합판 (Front Wall)', cost: '$0.8', spec: '720x45x4mm Front Panel' },
      backWall: { group: new THREE.Group(), baseY: 0.195, name: '후면 측판 자작합판 (Back Wall)', cost: '$0.8', spec: '720x45x4mm Back Panel' },
      leftWall: { group: new THREE.Group(), baseX: -0.360, name: '좌측 측판 자작합판 (Left Wall)', cost: '$0.5', spec: '382x45x4mm Left Panel' },
      rightWall: { group: new THREE.Group(), baseX: 0.360, name: '우측 측판 자작합판 (Right Wall)', cost: '$0.5', spec: '382x45x4mm Right Panel' },

      cornerBrackets: { group: new THREE.Group(), baseZ: 0.0, name: '코너 L-자 강철 체결 브래킷 (4개)', cost: '$1.0', spec: 'Steel L-Bracket 20x20mm' },
      internalRibs: { group: new THREE.Group(), baseZ: 0.0, name: '내부 격자보 보강 리브 (Cross Reinforcement Ribs)', cost: '$0.8', spec: '12x20mm Birch Rib Grid (Center Cross)' },
      bottomPlate: { group: new THREE.Group(), baseZ: -0.032, name: '하판 자작합판 (4mm Birch Plywood)', cost: '$1.2', spec: '720x390x4mm Bottom Base' },
      bolts: { group: new THREE.Group(), baseZ: -0.045, name: 'M3 체결 볼트 & 황동 스페이서 (8개)', cost: '$0.7', spec: 'M3x12 Stainless Bolts + H6 Standoffs' }
    };

    this.selectedPartInfo = null;

    this.init3D();
    this.buildAssembly();
    this.initEvents();
    this.animate();
  }

  init3D() {
    if (!this.container || typeof THREE === 'undefined') return;

    const w = this.container.clientWidth || 800;
    const h = this.container.clientHeight || 500;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x060913);

    this.camera = new THREE.PerspectiveCamera(40, w / h, 0.05, 50);
    this.camera.position.set(1.1, -1.3, 0.9);
    this.camera.lookAt(0, 0, 0);

    const ambLight = new THREE.AmbientLight(0xffffff, 0.85);
    this.scene.add(ambLight);

    const dirLight1 = new THREE.DirectionalLight(0x38bdf8, 1.3);
    dirLight1.position.set(3, 4, 5);
    this.scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xec4899, 0.8);
    dirLight2.position.set(-3, -2, 3);
    this.scene.add(dirLight2);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(w, h);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    if (typeof THREE.OrbitControls !== 'undefined') {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.maxPolarAngle = Math.PI / 2 + 0.25;
    }

    const grid = new THREE.GridHelper(3.0, 30, 0x1e293b, 0x0f172a);
    grid.rotation.x = Math.PI / 2;
    grid.position.z = -0.18;
    this.scene.add(grid);

    Object.values(this.layers).forEach(layer => {
      this.scene.add(layer.group);
    });
  }

  buildAssembly() {
    const pW = 0.72; // 720mm (Fits Standard 750mm Acrylic Basket)
    const pH = 0.39; // 390mm (Fits Standard 420mm Acrylic Basket)
    const pD = 0.045; // 45mm Box Depth
    const pT = 0.004; // 4mm Thickness

    const woodMat = new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.55, metalness: 0.1 });
    const sideWoodMat = new THREE.MeshStandardMaterial({ color: 0xb45309, roughness: 0.6, metalness: 0.1 });

    // 0. Washable Fabric Sleeve Cover (10s Snap-on)
    const sleeveMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.7, opacity: 0.85, transparent: true });
    const sleeveGeom = new THREE.BoxGeometry(pW + 0.008, pH + 0.008, 0.003);
    const sleeveMesh = new THREE.Mesh(sleeveGeom, sleeveMat);
    sleeveMesh.userData = { layerKey: 'washableSleeve' };
    this.layers.washableSleeve.group.add(sleeveMesh);

    // 1. Top Plate (800x450x4mm)
    const topGeom = new THREE.BoxGeometry(pW, pH, pT);
    const topMesh = new THREE.Mesh(topGeom, woodMat);
    topMesh.userData = { layerKey: 'topPlate' };
    this.layers.topPlate.group.add(topMesh);

    // 2. EVA Foam Gasket Frame
    const evaMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.9 });
    const evaGeom = new THREE.BoxGeometry(pW - 0.01, pH - 0.01, 0.006);
    const evaMesh = new THREE.Mesh(evaGeom, evaMat);
    evaMesh.userData = { layerKey: 'evaGasket' };
    this.layers.evaGasket.group.add(evaMesh);

    // 3. TEAX14C02 Exciters (4 Units)
    const exciterPos = [
      { x: -0.22, y: -0.12 }, { x: 0.22, y: -0.12 },
      { x: -0.22, y: 0.12 }, { x: 0.22, y: 0.12 }
    ];

    exciterPos.forEach(pos => {
      const exciterGroup = this.createExciter3DModel();
      exciterGroup.position.set(pos.x, pos.y, 0);
      exciterGroup.userData = { layerKey: 'exciters' };
      this.layers.exciters.group.add(exciterGroup);
    });

    // 4. Control Box Enclosure & PCB
    const cboxGroup = this.createControlBox3DModel();
    cboxGroup.userData = { layerKey: 'controlBox' };
    this.layers.controlBox.group.add(cboxGroup);

    // 5. 4 Side Walls (Box Enclosure Walls)
    // Front & Back Walls (800 x 60 x 4mm)
    const fbWallGeom = new THREE.BoxGeometry(pW, pT, pD);
    const frontWallMesh = new THREE.Mesh(fbWallGeom, sideWoodMat);
    frontWallMesh.userData = { layerKey: 'frontWall' };
    this.layers.frontWall.group.add(frontWallMesh);

    const backWallMesh = new THREE.Mesh(fbWallGeom, sideWoodMat.clone());
    backWallMesh.userData = { layerKey: 'backWall' };
    this.layers.backWall.group.add(backWallMesh);

    // Left & Right Walls (442 x 60 x 4mm)
    const lrWallGeom = new THREE.BoxGeometry(pT, pH - pT * 2, pD);
    const leftWallMesh = new THREE.Mesh(lrWallGeom, sideWoodMat.clone());
    leftWallMesh.userData = { layerKey: 'leftWall' };
    this.layers.leftWall.group.add(leftWallMesh);

    const rightWallMesh = new THREE.Mesh(lrWallGeom, sideWoodMat.clone());
    rightWallMesh.userData = { layerKey: 'rightWall' };
    this.layers.rightWall.group.add(rightWallMesh);

    // 6. Corner L-Brackets (4 Corners - Scaled to 720x390mm Box Inner Corners)
    const bracketMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.95, roughness: 0.15 });
    const bracketPos = [
      { x: -0.34, y: -0.175 }, { x: 0.34, y: -0.175 },
      { x: -0.34, y: 0.175 }, { x: 0.34, y: 0.175 }
    ];
    bracketPos.forEach(bpos => {
      const bGeom = new THREE.BoxGeometry(0.02, 0.02, 0.035);
      const bMesh = new THREE.Mesh(bGeom, bracketMat);
      bMesh.position.set(bpos.x, bpos.y, 0);
      bMesh.userData = { layerKey: 'cornerBrackets' };
      this.layers.cornerBrackets.group.add(bMesh);
    });

    // 6.5 Internal Cross Reinforcement Ribs (Center Rib Grid)
    const ribMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.4, metalness: 0.2 });
    const ribXGeom = new THREE.BoxGeometry(pW * 0.70, 0.012, 0.020);
    const ribYGeom = new THREE.BoxGeometry(0.012, pH * 0.70, 0.020);
    
    const ribXMesh = new THREE.Mesh(ribXGeom, ribMat);
    ribXMesh.position.set(0, 0, 0);
    ribXMesh.userData = { layerKey: 'internalRibs' };
    this.layers.internalRibs.group.add(ribXMesh);

    const ribYMesh = new THREE.Mesh(ribYGeom, ribMat.clone());
    ribYMesh.position.set(0, 0, 0);
    ribYMesh.userData = { layerKey: 'internalRibs' };
    this.layers.internalRibs.group.add(ribYMesh);

    // 7. Bottom Plate (720x390x4mm)
    const botMesh = new THREE.Mesh(topGeom, woodMat.clone());
    botMesh.userData = { layerKey: 'bottomPlate' };
    this.layers.bottomPlate.group.add(botMesh);

    // 8. M3 Bolts & Brass Standoffs (8 Points - Scaled Inside 720x390mm Margins)
    const boltPositions = [
      { x: -0.32, y: -0.165 }, { x: 0.0, y: -0.165 }, { x: 0.32, y: -0.165 },
      { x: -0.32, y: 0.165 }, { x: 0.0, y: 0.165 }, { x: 0.32, y: 0.165 },
      { x: -0.32, y: 0.0 }, { x: 0.32, y: 0.0 }
    ];

    boltPositions.forEach(bpos => {
      const boltMesh = this.createM3Bolt3DModel();
      boltMesh.position.set(bpos.x, bpos.y, 0);
      boltMesh.userData = { layerKey: 'bolts' };
      this.layers.bolts.group.add(boltMesh);
    });

    this.updateExplodedPositions();
  }

  createExciter3DModel() {
    const group = new THREE.Group();
    const magGeom = new THREE.CylinderGeometry(0.025, 0.025, 0.012, 24);
    const magMat = new THREE.MeshStandardMaterial({ color: 0xec4899, metalness: 0.8, roughness: 0.2 });
    const magMesh = new THREE.Mesh(magGeom, magMat);
    magMesh.rotation.x = Math.PI / 2;
    group.add(magMesh);

    const ringGeom = new THREE.TorusGeometry(0.028, 0.003, 16, 32);
    const ringMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
    const ringMesh = new THREE.Mesh(ringGeom, ringMat);
    group.add(ringMesh);

    const tapeGeom = new THREE.CylinderGeometry(0.024, 0.024, 0.0015, 24);
    const tapeMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.5 });
    const tapeMesh = new THREE.Mesh(tapeGeom, tapeMat);
    tapeMesh.position.z = 0.007;
    tapeMesh.rotation.x = Math.PI / 2;
    group.add(tapeMesh);

    return group;
  }

  createControlBox3DModel() {
    const group = new THREE.Group();
    const boxGeom = new THREE.BoxGeometry(0.14, 0.09, 0.025);
    const boxMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.4, metalness: 0.6 });
    const boxMesh = new THREE.Mesh(boxGeom, boxMat);
    group.add(boxMesh);

    const pcbGeom = new THREE.BoxGeometry(0.12, 0.07, 0.002);
    const pcbMat = new THREE.MeshStandardMaterial({ color: 0x10b981, roughness: 0.3, metalness: 0.5 });
    const pcbMesh = new THREE.Mesh(pcbGeom, pcbMat);
    pcbMesh.position.z = 0.014;
    group.add(pcbMesh);

    const hsGeom = new THREE.BoxGeometry(0.025, 0.025, 0.008);
    const hsMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.9, roughness: 0.1 });
    const hsMesh = new THREE.Mesh(hsGeom, hsMat);
    hsMesh.position.set(-0.02, 0.01, 0.018);
    group.add(hsMesh);

    const usbGeom = new THREE.BoxGeometry(0.012, 0.006, 0.004);
    const usbMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, metalness: 0.9 });
    const usbMesh = new THREE.Mesh(usbGeom, usbMat);
    usbMesh.position.set(0.065, 0, 0.005);
    group.add(usbMesh);

    return group;
  }

  createM3Bolt3DModel() {
    const group = new THREE.Group();
    const capGeom = new THREE.CylinderGeometry(0.004, 0.004, 0.004, 16);
    const boltMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.9, roughness: 0.2 });
    const capMesh = new THREE.Mesh(capGeom, boltMat);
    capMesh.rotation.x = Math.PI / 2;
    capMesh.position.z = 0.045;
    group.add(capMesh);

    const shaftGeom = new THREE.CylinderGeometry(0.0018, 0.0018, 0.08, 12);
    const shaftMesh = new THREE.Mesh(shaftGeom, boltMat);
    shaftMesh.rotation.x = Math.PI / 2;
    group.add(shaftMesh);

    const standoffGeom = new THREE.CylinderGeometry(0.0035, 0.0035, 0.012, 6);
    const standoffMat = new THREE.MeshStandardMaterial({ color: 0xeab308, metalness: 0.8, roughness: 0.3 });
    const standoffMesh = new THREE.Mesh(standoffGeom, standoffMat);
    standoffMesh.rotation.x = Math.PI / 2;
    standoffMesh.position.z = 0.01;
    group.add(standoffMesh);

    return group;
  }

  setExplodedFactor(factor) {
    this.explodedFactor = Math.max(0.0, Math.min(1.0, factor));
    this.updateExplodedPositions();
  }

  // 6-Directional Box Exploded View Offsets (Top/Bottom + 4 Side Walls)
  updateExplodedPositions() {
    const expandStepZ = 0.16; // Vertical offset
    const expandStepXY = 0.18; // Horizontal 4 side wall offset

    // Vertical Top/Bottom Layers
    this.layers.washableSleeve.group.position.z = this.layers.washableSleeve.baseZ + this.explodedFactor * (expandStepZ * 3.2);
    this.layers.topPlate.group.position.z = this.layers.topPlate.baseZ + this.explodedFactor * (expandStepZ * 2.5);
    this.layers.evaGasket.group.position.z = this.layers.evaGasket.baseZ + this.explodedFactor * (expandStepZ * 1.6);
    this.layers.exciters.group.position.z = this.layers.exciters.baseZ + this.explodedFactor * (expandStepZ * 0.8);
    this.layers.controlBox.group.position.z = this.layers.controlBox.baseZ;
    this.layers.cornerBrackets.group.position.z = this.layers.cornerBrackets.baseZ;
    this.layers.bottomPlate.group.position.z = this.layers.bottomPlate.baseZ - this.explodedFactor * (expandStepZ * 1.2);
    this.layers.bolts.group.position.z = this.layers.bolts.baseZ - this.explodedFactor * (expandStepZ * 2.2);

    // 4 Side Walls Horizontal Explosion (Front, Back, Left, Right)
    this.layers.frontWall.group.position.y = this.layers.frontWall.baseY - this.explodedFactor * expandStepXY;
    this.layers.backWall.group.position.y = this.layers.backWall.baseY + this.explodedFactor * expandStepXY;
    this.layers.leftWall.group.position.x = this.layers.leftWall.baseX - this.explodedFactor * expandStepXY;
    this.layers.rightWall.group.position.x = this.layers.rightWall.baseX + this.explodedFactor * expandStepXY;
  }

  setLayerVisibility(layerKey, visible) {
    if (this.layers[layerKey]) {
      this.layers[layerKey].group.visible = visible;
    }
  }

  initEvents() {
    if (!this.container) return;

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    this.container.addEventListener('click', (e) => {
      const rect = this.container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, this.camera);
      const intersects = raycaster.intersectObjects(this.scene.children, true);

      if (intersects.length > 0) {
        let current = intersects[0].object;
        while (current && !current.userData.layerKey && current.parent) {
          current = current.parent;
        }

        if (current && current.userData.layerKey) {
          const lkey = current.userData.layerKey;
          this.selectedPartInfo = this.layers[lkey];
          if (window.onCADPartSelect) window.onCADPartSelect(this.selectedPartInfo);
        }
      }
    });
  }

  animate(t = 0) {
    requestAnimationFrame((time) => this.animate(time));

    if (this.controls) {
      this.controls.update();
    }

    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  }
}

if (typeof window !== 'undefined') {
  window.CADAssemblyViewer = CADAssemblyViewer;
}
