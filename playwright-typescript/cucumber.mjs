export default {
  paths: ["features/**/*.feature"],
  require: ["dist/support/**/*.js", "dist/steps/**/*.js"],
  format: ["progress", "html:reports/cucumber-report.html"],
  parallel: 1,
  retry: 0
};
