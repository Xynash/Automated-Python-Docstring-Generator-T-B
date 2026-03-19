import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {

    console.log('Docgen extension is now active!');

    const disposable = vscode.commands.registerCommand('docgen-extension.generateDocs', async () => {

        const editor = vscode.window.activeTextEditor;

        if (!editor) {
            vscode.window.showErrorMessage("No active Python file open.");
            return;
        }

        const code = editor.document.getText();

        try {
            const response = await axios.post("http://127.0.0.1:8000/process", {
                code: code
            });

            const documentedCode = response.data.documented_code;

            const fullRange = new vscode.Range(
                editor.document.positionAt(0),
                editor.document.positionAt(code.length)
            );

            await editor.edit(editBuilder => {
                editBuilder.replace(fullRange, documentedCode);
            });

            vscode.window.showInformationMessage("Docstrings generated successfully!");

        } catch (error) {
            vscode.window.showErrorMessage("Cannot connect to FastAPI backend. Is server running?");
        }
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}