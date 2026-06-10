import { createLayout } from "./layout";
import { getPreferredLanguage, setPreferredLanguage } from "./preferences.store";
import { dispatch, installRouter } from "./router";

export function bootstrap(): void {
  const root = document.querySelector<HTMLElement>("#app");
  if (!root) throw new Error("Missing #app root");

  const initialLanguage = getPreferredLanguage();
  document.documentElement.lang = initialLanguage;

  const layout = createLayout(root, initialLanguage, (language) => {
    setPreferredLanguage(language);
    document.documentElement.lang = language;
    void dispatch(new URL(window.location.href), layout);
  });

  installRouter(layout);
  void dispatch(new URL(window.location.href), layout);
}
