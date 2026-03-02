import "@testing-library/jest-dom/vitest";

// Mock ResizeObserver (used by Radix UI components like Select, Slider)
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver;

// Mock pointer capture methods (used by Radix UI Select)
if (!Element.prototype.hasPointerCapture) {
  Element.prototype.hasPointerCapture = () => false;
}
if (!Element.prototype.setPointerCapture) {
  Element.prototype.setPointerCapture = () => {};
}
if (!Element.prototype.releasePointerCapture) {
  Element.prototype.releasePointerCapture = () => {};
}

// Mock scrollIntoView (used by Radix UI)
if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = () => {};
}
