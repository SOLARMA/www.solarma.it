// Config for Super-linter's ESLint check (VALIDATE_JAVASCRIPT_ES). Deliberately
// self-contained -- no imports -- so it doesn't depend on what else happens to
// be resolvable inside the linter's environment. assets/js/site.js is plain
// browser JS with no build step, hence sourceType "script" rather than "module".
export default [
  {
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: "script",
      globals: { window: "readonly", document: "readonly" },
    },
    rules: {
      "no-undef": "error",
      "no-unused-vars": "error",
      "no-redeclare": "error",
      "no-dupe-keys": "error",
      "no-dupe-args": "error",
      "no-unreachable": "error",
      "no-const-assign": "error",
      "no-fallthrough": "error",
      "no-irregular-whitespace": "error",
      "use-isnan": "error",
      "valid-typeof": "error",
    },
  },
];
