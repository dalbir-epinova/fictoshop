export const settings = {
  baseUrl: (process.env.FICTOSHOP_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, ""),
  headed: process.env.HEADED?.toLowerCase() !== "false",
  timeout: 10_000
};
