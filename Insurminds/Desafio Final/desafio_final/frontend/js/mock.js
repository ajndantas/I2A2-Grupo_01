const suppliers = ["Carboxi Indústria e Comércio", "J. T. Indústria de Cafés", "Companhia Brasileira de Educação", "V Caldi Peças e Serviços", "Fornecedor Nacional Ltda."];
const values = [1254300.42, 986740.3, 764210.15, 589630.0, 421580.78];

export function createDemoDatasets(files) {
  const datasetIds = files.map((file, index) => `demo_${Date.now()}_${index + 1}`);

  return {
    dataset_ids: datasetIds,
    filenames: files.map(file => file.name),
    status: "ready",
    files: files.map((file, index) => ({
      name: file.name,
      dataset_id: datasetIds[index],
      size: file.size
    }))
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
    answer: "As bases foram processadas e estão prontas para análise. Posso comparar fornecedores, calcular valores, classificar produtos, analisar CFOPs e identificar concentrações por estado.",
    type: "text"
  };
}

function currency(value) {
  return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}
