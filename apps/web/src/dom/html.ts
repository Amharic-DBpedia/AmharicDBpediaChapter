export function clear(node: Element): void {
  while (node.firstChild) node.firstChild.remove();
}

export function text(tagName: keyof HTMLElementTagNameMap, value: string): HTMLElement {
  const element = document.createElement(tagName);
  element.textContent = value;
  return element;
}

export function externalLink(href: string, label: string): HTMLAnchorElement {
  const anchor = document.createElement("a");
  anchor.href = href;
  anchor.target = "_blank";
  anchor.rel = "noopener noreferrer";
  anchor.textContent = label;
  return anchor;
}

export function iconButton(label: string, symbol: string): HTMLButtonElement {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "icon-button";
  button.title = label;
  button.setAttribute("aria-label", label);
  button.textContent = symbol;
  return button;
}
