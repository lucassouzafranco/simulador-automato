export interface Margin {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

export interface Dimensions {
  width: number;
  height: number;
  margin: Margin;
  innerWidth: number;
  innerHeight: number;
}

export function getDimensions(
  width: number,
  height: number,
  margin: Margin = { top: 20, right: 20, bottom: 30, left: 40 }
): Dimensions {
  return {
    width,
    height,
    margin,
    innerWidth: width - margin.left - margin.right,
    innerHeight: height - margin.top - margin.bottom,
  };
}
