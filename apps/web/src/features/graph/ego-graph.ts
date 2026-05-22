import type { EgoGraph, Iri } from "@amdb/core";

interface Point {
  readonly x: number;
  readonly y: number;
}

export function renderEgoGraph(graph: EgoGraph, centerId: Iri): HTMLElement {
  const figure = document.createElement("figure");
  figure.className = "graph-panel";

  const canvas = document.createElement("canvas");
  canvas.width = 860;
  canvas.height = 360;
  canvas.ariaLabel = "One-hop resource graph";

  const caption = document.createElement("figcaption");
  caption.textContent = "Bounded one-hop resource graph";

  figure.append(canvas, caption);
  draw(canvas, graph, centerId);
  return figure;
}

function draw(canvas: HTMLCanvasElement, graph: EgoGraph, centerId: Iri): void {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const center: Point = { x: canvas.width / 2, y: canvas.height / 2 };
  const outer = graph.nodes.filter((node) => node.id !== centerId);
  const positions = new Map<string, Point>([[centerId, center]]);

  outer.forEach((node, index) => {
    const angle = (Math.PI * 2 * index) / Math.max(outer.length, 1);
    const radius = Math.min(canvas.width, canvas.height) * 0.34;
    positions.set(node.id, {
      x: center.x + Math.cos(angle) * radius,
      y: center.y + Math.sin(angle) * radius,
    });
  });

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.font = "13px system-ui, sans-serif";
  ctx.lineWidth = 1;
  ctx.strokeStyle = "#90a4ae";

  for (const edge of graph.edges) {
    const from = positions.get(edge.from);
    const to = positions.get(edge.to);
    if (!from || !to) continue;
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.lineTo(to.x, to.y);
    ctx.stroke();
  }

  for (const node of graph.nodes) {
    const position = positions.get(node.id);
    if (!position) continue;
    const isCenter = node.id === centerId;
    ctx.fillStyle = isCenter ? "#005f73" : "#9b5de5";
    ctx.beginPath();
    ctx.arc(position.x, position.y, isCenter ? 12 : 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#1f2933";
    ctx.fillText(trimLabel(node.label), position.x + 14, position.y + 5);
  }
}

function trimLabel(label: string): string {
  return label.length > 24 ? `${label.slice(0, 21)}...` : label;
}
