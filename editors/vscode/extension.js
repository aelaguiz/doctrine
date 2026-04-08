const vscode = require("vscode");

const {
  provideDefinitionLinks,
  provideImportLinks,
} = require("./resolver");

const DOCTRINE_SELECTOR = { language: "doctrine" };

function activate(context) {
  context.subscriptions.push(
    vscode.languages.registerDocumentLinkProvider(DOCTRINE_SELECTOR, {
      provideDocumentLinks(document, token) {
        return provideImportLinks(document, token);
      },
    }),
    vscode.languages.registerDefinitionProvider(DOCTRINE_SELECTOR, {
      provideDefinition(document, position, token) {
        return provideDefinitionLinks(document, position, token);
      },
    }),
  );
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
