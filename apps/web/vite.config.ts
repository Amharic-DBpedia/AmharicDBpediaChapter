import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";

export default defineConfig({
  resolve: {
    alias: {
      "@amdb/core": fileURLToPath(new URL("../../packages/core/src/index.ts", import.meta.url)),
      "@amdb/content": fileURLToPath(
        new URL("../../packages/content/src/index.ts", import.meta.url),
      ),
    },
  },
});
