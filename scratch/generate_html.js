const fs = require('fs');

const mdFile = 'C:\\Users\\jamerson.jpd\\Desktop\\SENTINELA\\Documentacao_Completa_SENTINELA.md';
const htmlFile = 'C:\\Users\\jamerson.jpd\\Desktop\\SENTINELA\\Documentacao_Completa_SENTINELA.html';

const mdContent = fs.readFileSync(mdFile, 'utf-8');

// Very simple conversion for presentation purposes if marked is not available
// We'll just fetch a CDN script to render it in the browser!
const htmlContent = `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Documentação Completa - SENTINELA</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 40px; }
        h1, h2, h3 { color: #1a202c; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #cbd5e0; padding: 10px; text-align: left; }
        th { background-color: #f7fafc; font-weight: bold; }
        code { background-color: #edf2f7; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
        pre { background-color: #edf2f7; padding: 15px; border-radius: 6px; overflow-x: auto; }
        blockquote { border-left: 4px solid #3182ce; margin: 0; padding-left: 15px; color: #4a5568; }
        @media print {
            body { padding: 0; max-width: 100%; }
            .no-print { display: none; }
        }
    </style>
</head>
<body>
    <div class="no-print" style="background: #ebf8fa; padding: 15px; border: 1px solid #b2e6ef; border-radius: 6px; margin-bottom: 20px;">
        <strong>💡 Dica:</strong> Para gerar o PDF definitivo, aperte <b>Ctrl + P</b> (ou Cmd + P) e escolha "Salvar como PDF".
    </div>
    <div id="content">Carregando documento...</div>

    <script>
        const markdown = \`${mdContent.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`;
        document.getElementById('content').innerHTML = marked.parse(markdown);
    </script>
</body>
</html>
`;

fs.writeFileSync(htmlFile, htmlContent);
console.log('HTML file created!');
