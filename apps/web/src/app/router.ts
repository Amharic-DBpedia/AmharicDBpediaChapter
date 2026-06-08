import type { AppLayout } from "./layout";

type RouteHandler = (
  params: Record<string, string>,
  url: URL,
  layout: AppLayout,
) => Promise<void> | void;

interface RouteDefinition {
  readonly pathname: string;
  readonly handler: RouteHandler;
}

interface NativeURLPattern {
  exec(input: { pathname: string }): {
    readonly pathname: { readonly groups: Record<string, string | undefined> };
  } | null;
}

type NativeURLPatternConstructor = new (pattern: { pathname: string }) => NativeURLPattern;

const routes: readonly RouteDefinition[] = [
  {
    pathname: "/",
    handler: (_params, _url, layout) =>
      import("../routes/home.route").then((m) => m.renderHome(layout)),
  },
  {
    pathname: "/datasets",
    handler: (_params, _url, layout) =>
      import("../routes/datasets.route").then((m) => m.renderDatasets(layout)),
  },
  {
    pathname: "/news",
    handler: (_params, _url, layout) =>
      import("../routes/news.route").then((m) => m.renderNews(layout)),
  },
  {
    pathname: "/statistics",
    handler: (_params, _url, layout) =>
      import("../routes/statistics.route").then((m) => m.renderStatistics(layout)),
  },
  {
    pathname: "/query",
    handler: (_params, _url, layout) =>
      import("../routes/query.route").then((m) => m.renderQuery(layout)),
  },
  {
    pathname: "/sparql",
    handler: (_params, _url, layout) =>
      import("../routes/query.route").then((m) => m.renderQuery(layout)),
  },
  {
    pathname: "/team",
    handler: (_params, _url, layout) =>
      import("../routes/team.route").then((m) => m.renderTeam(layout)),
  },
  {
    pathname: "/docs",
    handler: (_params, _url, layout) =>
      import("../routes/docs.route").then((m) => m.renderDocs(layout)),
  },
  {
    pathname: "/resource/:title",
    handler: (params, _url, layout) =>
      import("../routes/resource.route").then((m) => m.renderResource(layout, params.title ?? "")),
  },
];

export function installRouter(layout: AppLayout): void {
  window.addEventListener("popstate", () => {
    void dispatch(new URL(window.location.href), layout);
  });

  document.addEventListener("click", (event) => {
    const target = event.target as HTMLElement | null;
    const anchor = target?.closest("a[href]") as HTMLAnchorElement | null;
    if (!anchor) return;
    if (anchor.target || anchor.origin !== window.location.origin) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

    event.preventDefault();
    void navigate(anchor.href, layout);
  });
}

export async function navigate(href: string, layout: AppLayout, replace = false): Promise<void> {
  const url = new URL(href, window.location.origin);
  if (replace) history.replaceState({}, "", url);
  else history.pushState({}, "", url);
  await dispatch(url, layout);
}

export async function dispatch(url: URL, layout: AppLayout): Promise<void> {
  for (const route of routes) {
    const match = matchPath(route.pathname, url.pathname);
    if (!match) continue;
    await route.handler(match, url, layout);
    layout.main.focus({ preventScroll: true });
    return;
  }

  const { renderNotFound } = await import("../routes/not-found.route");
  renderNotFound(layout);
}

function matchPath(pattern: string, pathname: string): Record<string, string> | null {
  const URLPatternCtor = (window as Window & { URLPattern?: NativeURLPatternConstructor })
    .URLPattern;
  if (URLPatternCtor) {
    const match = new URLPatternCtor({ pathname: pattern }).exec({ pathname });
    if (match) {
      return Object.fromEntries(
        Object.entries(match.pathname.groups).filter(
          (entry): entry is [string, string] => typeof entry[1] === "string",
        ),
      );
    }
  }

  const patternParts = pattern.split("/").filter(Boolean);
  const pathParts = pathname.split("/").filter(Boolean);
  if (patternParts.length !== pathParts.length) return null;

  const params: Record<string, string> = {};
  for (const [index, patternPart] of patternParts.entries()) {
    const pathPart = pathParts[index];
    if (!pathPart) return null;
    if (patternPart.startsWith(":")) {
      params[patternPart.slice(1)] = decodeURIComponent(pathPart);
      continue;
    }
    if (patternPart !== pathPart) return null;
  }

  return params;
}
