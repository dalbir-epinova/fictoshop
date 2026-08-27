export interface Credentials {
  username: string;
  password: string;
  superuser?: boolean;
}

export interface ProductRecord {
  id: number;
  name: string;
  description: string;
  price: number;
  in_stock: number;
}

export interface ReviewRecord {
  id: number;
  user: string;
  rating: number;
  comment: string;
}

export interface OrderItemRecord {
  product_name: string;
  unit_price: number;
  quantity: number;
  line_total: number;
}

export interface OrderRecord {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  address: string;
  postal_code: string;
  city: string;
  country: string;
  total_amount: number;
  items: OrderItemRecord[];
}

export interface DatabaseSnapshot {
  orders: number[];
  reviews: number[];
  products: number[];
  users: number[];
}

export interface ApiResponse {
  status: number;
  text: string;
  json: unknown;
}

export interface ScenarioState {
  products: Record<string, ProductRecord>;
  shipping: Record<string, string>;
  admin?: Credentials;
  user?: Credentials;
  review?: ReviewRecord;
  order?: OrderRecord;
  response?: ApiResponse;
  selectedProductName: string;
  searchQuery: string;
  reviewComment: string;
  updatedReviewComment: string;
  rating: number;
  updatedRating: number;
  initialProductCount: number;
  initialOrderCount: number;
  initialStock: number;
  initialSecondaryStock: number;
  lastBrowserStatus?: number;
  lastBrowserBody: string;
  requestedUrls: string[];
  configuredIosBase: string;
  expectedItems: OrderItemRecord[];
  removedProductName: string;
}

export function newScenarioState(): ScenarioState {
  return {
    products: {},
    shipping: {},
    selectedProductName: "",
    searchQuery: "",
    reviewComment: `Playwright review ${crypto.randomUUID()}`.slice(0, 34),
    updatedReviewComment: `Updated Playwright review ${crypto.randomUUID()}`.slice(0, 42),
    rating: 4,
    updatedRating: 5,
    initialProductCount: 0,
    initialOrderCount: 0,
    initialStock: 0,
    initialSecondaryStock: 0,
    lastBrowserBody: "",
    requestedUrls: [],
    configuredIosBase: "http://127.0.0.1:8000",
    expectedItems: [],
    removedProductName: ""
  };
}
