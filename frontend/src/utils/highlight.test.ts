import { describe, expect, test } from "vitest";
import { highlightQuery, getStatusLabel } from "./highlight";

describe("highlightQuery", () => {
  test("highlights matching words case-insensitively", () => {
    const result = highlightQuery(
      "Python является популярным языком программирования",
      "python",
    );
    expect(result).toContain('<mark class="highlight">Python</mark>');
  });

  test("highlights multiple query words", () => {
    const result = highlightQuery("Python and Java are languages", "python java");
    expect(result).toContain('<mark class="highlight">Python</mark>');
    expect(result).toContain('<mark class="highlight">Java</mark>');
  });
});

describe("getStatusLabel", () => {
  test("returns localized labels", () => {
    expect(getStatusLabel("ready")).toBe("Готово");
    expect(getStatusLabel("indexing")).toBe("Индексация...");
  });
});
