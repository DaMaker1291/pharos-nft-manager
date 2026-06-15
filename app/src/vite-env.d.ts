interface Window {
  ethereum?: import("ethers").Eip1193Provider & {
    isMetaMask?: boolean;
    on?: (event: string, cb: (...args: any[]) => void) => void;
    removeListener?: (event: string, cb: (...args: any[]) => void) => void;
    request: (args: { method: string; params?: any[] }) => Promise<any>;
  };
}

declare module "ethers" {
  interface Eip1193Provider {
    request: (args: { method: string; params?: any[] }) => Promise<any>;
  }
}
