import { setWorldConstructor, World, type IWorldOptions } from "@cucumber/cucumber";
import type { Browser, BrowserContext, Page } from "@playwright/test";
import { DjangoTestData } from "./django-test-data.js";
import { newScenarioState, type DatabaseSnapshot, type ScenarioState } from "./models.js";
import { StorefrontApi } from "./storefront-api.js";

export class FictoshopWorld extends World {
  browser?: Browser;
  context?: BrowserContext;
  page!: Page;
  data = new DjangoTestData();
  api = new StorefrontApi();
  state: ScenarioState = newScenarioState();
  snapshot?: DatabaseSnapshot;

  constructor(options: IWorldOptions) {
    super(options);
  }
}

setWorldConstructor(FictoshopWorld);
