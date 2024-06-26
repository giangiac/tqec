/* eslint-disable max-len */
/* eslint-disable guard-for-in */
/* eslint-disable no-restricted-syntax */
import { Graphics } from 'pixi.js';
import GridUnit from './GridUnit';

export default class Grid extends Graphics {
  constructor(gridSize, workspace, app) {
    super();
    this.lineStyle(1, 'black');
    for (let x = 0; x <= app.screen.width; x += gridSize) {
      this.moveTo(x, 0);
      this.lineTo(x, app.screen.height);
    }

    // Draw horizontal lines
    for (let y = 0; y <= app.screen.height; y += gridSize) {
      this.moveTo(0, y);
      this.lineTo(app.screen.width, y);
    }

    // Add this squares for recoloration upon highlighting
    this.units = [];
    for (let x = 0; x <= app.screen.width; x += gridSize) {
      this.units[x] = [];
      for (let y = 0; y <= app.screen.height; y += gridSize) {
        const unit = new GridUnit(x, y, gridSize, workspace, app);
        this.units[x][y] = unit;
      }
    }
    this.name = 'Grid';
    this.interactive = true;
    this.gridSize = gridSize;
  }

  visibleUnits = () => this.units.flat().filter((unit) => unit.visible);

  footprintWidth = () => {
    const selectedUnits = this.visibleUnits();
    return Math.max(...selectedUnits.map((unit) => unit.x)) - Math.min(...selectedUnits.map((unit) => unit.x)) + this.gridSize;
  };

  footprintHeight = () => {
    const selectedUnits = this.visibleUnits();
    return Math.max(...selectedUnits.map((unit) => unit.y)) - Math.min(...selectedUnits.map((unit) => unit.y)) + this.gridSize;
  };

  selectedUnitsRectangular = () => {
    const selectedUnits = this.visibleUnits();
    this.xSorted = Array.from(new Set(selectedUnits.map((unit) => unit.x))).sort((a, b) => a.x - b.x);
    this.ySorted = Array.from(new Set(selectedUnits.map((unit) => unit.y))).sort((a, b) => a.y - b.y);
    return this.xSorted.length * this.ySorted.length === selectedUnits.length;
  };

  contains = (qubits) => {
    const unitXs = new Set(this.visibleUnits().map((unit) => [unit.x, unit.x + this.gridSize]).flat());
    const unitYs = new Set(this.visibleUnits().map((unit) => [unit.y, unit.y + this.gridSize]).flat());
    for (const qubit of qubits) {
      if (!unitXs.has(qubit.globalX) || !unitYs.has(qubit.globalY)) {
        return false;
      }
    }
    return true;
  };

  boundaryQubitsValid = (qubits) => {
    if (this.visibleUnits().length === 0) {
      throw new Error('No visible units in grid');
    }
    if (!this.selectedUnitsRectangular()) {
      return false;
    }
    const minX = Math.min(...this.visibleUnits().map((unit) => unit.x));
    const minY = Math.min(...this.visibleUnits().map((unit) => unit.y));
    for (const qubit of qubits) {
      qubit.applyBoundingBoxCoordinates(qubit.globalX - minX, qubit.globalY - minY);
    }
    // Check if boundary qubits overlap
    const xLeftboundaryQubits = new Set(qubits.filter((qubit) => qubit.bbX === 0).map((qubit) => qubit.bbY));
    const xLen = this.xSorted.length * this.gridSize;
    const xRightboundaryQubits = new Set(qubits.filter((qubit) => qubit.bbX === xLen).map((qubit) => qubit.bbY));
    if (xLeftboundaryQubits.intersection(xRightboundaryQubits).size > 0) {
      return false;
    }
    const yLen = this.ySorted.length * this.gridSize;
    const yboundaryQubits = new Set(qubits.filter((qubit) => qubit.bbY === 0).map((qubit) => qubit.bbX).flat());
    const yTopboundaryQubits = new Set(qubits.filter((qubit) => qubit.bbY === yLen).map((qubit) => qubit.bbX).flat());
    if (yboundaryQubits.intersection(yTopboundaryQubits).size > 0) {
      return false;
    }
    // Check if top left and bottom right corner qubits exist
    const upperLeftCornerQubit = qubits.filter((qubit) => qubit.bbX === 0 && qubit.bbY === 0);
    if (upperLeftCornerQubit.length === 1) {
      const bottomRightCornerQubit = qubits.filter((qubit) => qubit.bbX === xLen && qubit.bbY === yLen);
      if (bottomRightCornerQubit.length === 1) {
        return false;
      }
    }
    // Check if top right and bottom left corner qubits exist
    const upperRightCornerQubit = qubits.filter((qubit) => qubit.bbX === xLen && qubit.bbY === 0);
    if (upperRightCornerQubit.length === 1) {
      const bottomLeftCornerQubit = qubits.filter((qubit) => qubit.bbX === 0 && qubit.bbY === yLen);
      if (bottomLeftCornerQubit.length === 1) {
        return false;
      }
    }
    return true;
  };

  toString = () => this.name;
}
