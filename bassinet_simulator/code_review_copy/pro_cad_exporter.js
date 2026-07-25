/**
 * MAJN Housing CAE Studio Pro - Commercial CAD/CAE File Exporter Engine
 * Exports 3D Assemblies & Parts to Standard .OBJ and .STL formats for SolidWorks/Fusion360/CNC Machines.
 */

class CommercialCADExporter {
  constructor(cadViewer) {
    this.cadViewer = cadViewer;
  }

  // Export Scene Objects to Wavefront .OBJ Format
  exportToOBJ(filename = 'majn_bassinet_housing_3d.obj') {
    if (!this.cadViewer || !this.cadViewer.scene) return;

    let output = '# MAJN Housing CAE Studio Pro - 3D CAD Export\n';
    output += '# Generated for CNC Machining & SolidWorks / Fusion360\n\n';

    let vertexOffset = 1;

    this.cadViewer.scene.traverse((child) => {
      if (child.isMesh && child.visible) {
        const geom = child.geometry;
        if (!geom) return;

        output += `g ${child.name || child.userData.layerKey || 'mesh_part'}\n`;

        const pos = geom.attributes.position;
        if (!pos) return;

        // Apply World Matrix Transformation
        child.updateMatrixWorld(true);
        const matrix = child.matrixWorld;

        const v = new THREE.Vector3();
        for (let i = 0; i < pos.count; i++) {
          v.fromBufferAttribute(pos, i);
          v.applyMatrix4(matrix);
          output += `v ${v.x.toFixed(4)} ${v.y.toFixed(4)} ${v.z.toFixed(4)}\n`;
        }

        const index = geom.index;
        if (index) {
          for (let i = 0; i < index.count; i += 3) {
            output += `f ${index.getX(i) + vertexOffset} ${index.getY(i) + vertexOffset} ${index.getZ(i) + vertexOffset}\n`;
          }
        } else {
          for (let i = 0; i < pos.count; i += 3) {
            output += `f ${i + vertexOffset} ${i + 1 + vertexOffset} ${i + 2 + vertexOffset}\n`;
          }
        }

        vertexOffset += pos.count;
      }
    });

    this.downloadBlob(output, filename, 'text/plain');
  }

  // Helper: Trigger Browser Download
  downloadBlob(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

if (typeof window !== 'undefined') {
  window.CommercialCADExporter = CommercialCADExporter;
}
