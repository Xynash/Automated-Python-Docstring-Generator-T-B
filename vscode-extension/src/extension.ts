import * as vscode from 'vscode';
import fetch from 'node-fetch';

export function activate(context: vscode.ExtensionContext) {
    console.log('python-docgen extension is now active!');

    const disposable = vscode.commands.registerCommand('python-docgen.generate', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor detected!');
            return;
        }

        const code = editor.document.getText(editor.selection);
        if (!code) {
            vscode.window.showErrorMessage('Please select some Python code to generate docstrings.');
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, style: 'google' })
            });

            const data = await response.json();

            if (data.documented_code) {
                editor.edit(editBuilder => {
                    editBuilder.replace(editor.selection, data.documented_code);
                });
                vscode.window.showInformationMessage('Docstring generated successfully!');
            } else {
                vscode.window.showErrorMessage('Failed to generate docstring.');
            }

        } catch (err) {
            vscode.window.showErrorMessage('Error connecting to FastAPI backend.');
            console.error(err);
        }
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}