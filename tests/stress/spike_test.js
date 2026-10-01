import http from "k6/http";
import { check, sleep } from "k6";
import { SharedArray } from "k6/data";

// Cargar los PDFs de prueba
const pdfs = [
  open("../stress/pdfs/liviano.pdf", "b"),
  // Descomentar cuando tengas los otros PDFs:
  // open('../stress/pdfs/mediano.pdf', 'b'),
  // open('../stress/pdfs/pesado.pdf', 'b'),
  // open('../stress/pdfs/muy_pesado.pdf', 'b'),
];

const pdfNames = ["liviano.pdf", "mediano.pdf", "pesado.pdf", "muy_pesado.pdf"];

export const options = {
  stages: [
    { duration: "10s", target: 100 }, // Subida súbita a 100 VUs en 10s
    { duration: "20s", target: 100 }, // Sostenido a 100 VUs por 20s
    { duration: "10s", target: 0 }, // Rampa descendente en 10s
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"], // Menos de 1% de errores
    http_req_duration: ["p(95)<10000"], // P95 < 10s
  },
};

export default function () {
  const index = Math.floor(Math.random() * pdfs.length);
  const pdfData = pdfs[index];
  const pdfName = pdfNames[index] || "test.pdf";

  const payload = {
    file: http.file(pdfData, pdfName, "application/pdf"),
  };

  const res = http.post("http://localhost:8001/extract", payload);

  check(res, {
    "status es 200": (r) => r.status === 200,
    "tiene content": (r) => r.json("content") !== undefined,
    "tiene page_count": (r) => r.json("page_count") !== undefined,
  });
}
