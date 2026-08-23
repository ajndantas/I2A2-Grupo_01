const suppliers = ["Carboxi Indústria e Comércio", "J. T. Indústria de Cafés", "Companhia Brasileira de Educação", "V Caldi Peças e Serviços", "Fornecedor Nacional Ltda."];
const values = [1254300.42, 986740.3, 764210.15, 589630.0, 421580.78];

export function createDemoDataset(file) {
  const isLarge = file.name.includes("202505") || file.size > 50 * 1024 * 1024;
  return {
    dataset_id: `demo_${Date.now()}`,
    status: "ready",
    name: file.name,
    summary: {
      files: 2,
      invoices: isLarge ? 150976 : 100,
      items: isLarge ? 549431 : 565,
      period: isLarge ? "05/2025" : "01/2024",
      quality_score: isLarge ? 96 : 98,
      quality_message: "Estrutura consistente e relacionamento por chave de acesso.",
      detected_files: isLarge
        ? ["202505_NFe_NotaFiscal.csv", "202505_NFe_NotaFiscalItem.csv"]
        : ["202401_NFs_Cabecalho.csv", "202401_NFs_Itens.csv"]
    }
  };
}

export function answerDemoQuestion(question) {
  const normalized = question.toLocaleLowerCase("pt-BR");
  if (normalized.includes("fornecedor") || normalized.includes("emitente") || normalized.includes("maior")) {
    return {
      answer: "Os cinco maiores fornecedores concentram aproximadamente 42% do valor analisado. A Carboxi Indústria e Comércio ocupa a primeira posição, com R$ 1.254.300,42.",
      type: "mixed",
      table: {
        columns: ["Fornecedor", "Valor total", "Participação"],
        rows: suppliers.map((supplier, index) => [supplier, currency(values[index]), `${[13.2, 10.4, 8.1, 6.2, 4.4][index]}%`])
      },
      chart: { type: "bar", labels: suppliers, datasets: [{ label: "Valor total (R$)", data: values }] }
    };
  }
  if (normalized.includes("uf") || normalized.includes("estado")) {
    return {
      answer: "São Paulo apresenta o maior valor total, seguido por Minas Gerais e Paraná. Juntos, os três estados representam 55,8% da base.",
      type: "chart",
      chart: { type: "doughnut", labels: ["SP", "MG", "PR", "BA", "Outros"], datasets: [{ label: "Participação", data: [28.5, 16.2, 11.1, 8.7, 35.5] }] }
    };
  }
  if (normalized.includes("produto") || normalized.includes("item")) {
    return {
      answer: "O item com maior valor agregado foi Oxigênio Medicinal. A análise considera a soma do valor total registrado nas linhas de itens.",
      type: "table",
      table: { columns: ["Produto", "Quantidade", "Valor total"], rows: [["Oxigênio Medicinal", "1.284", "R$ 903.960,00"], ["Material educacional", "986", "R$ 522.500,00"], ["Peças automotivas", "744", "R$ 395.840,00"]] }
    };
  }
  return {
    answer: "A base foi processada e está pronta para análise. Posso comparar fornecedores, calcular valores, classificar produtos, analisar CFOPs e identificar concentrações por estado. Esta resposta é demonstrativa e será substituída pela análise real quando a API estiver conectada.",
    type: "text"
  };
}

function currency(value) {
  return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}
