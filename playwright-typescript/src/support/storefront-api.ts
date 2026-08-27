import { settings } from "./settings.js";
import type { ApiResponse } from "./models.js";

export class StorefrontApi {
  async request(method: string, path: string, body?: unknown): Promise<ApiResponse> {
    const response = await fetch(settings.baseUrl + path, {
      method,
      headers: body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body)
    });
    const text = await response.text();
    let json: unknown = null;
    try {
      json = text ? JSON.parse(text) : null;
    } catch {
      json = null;
    }
    return { status: response.status, text, json };
  }

  get(path: string): Promise<ApiResponse> {
    return this.request("GET", path);
  }

  post(path: string, body: unknown): Promise<ApiResponse> {
    return this.request("POST", path, body);
  }

  delete(path: string): Promise<ApiResponse> {
    return this.request("DELETE", path);
  }
}
