/// <reference types="vite/client" />

/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface Window {
  electronAPI: {
    getBackendPort: () => number;
    openFile: (path: string) => Promise<void>;
    selectDirectory: () => Promise<string | null>;
    selectFile: () => Promise<string | null>;
    openExternal: (url: string) => Promise<void>;
    restartBackend: () => Promise<void>;
  }
}

