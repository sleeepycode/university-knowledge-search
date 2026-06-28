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

test("returns original text when query is empty", () => {
  const result = highlightQuery("Some text", "");
  expect(result).toBe("Some text");
});

test("escapes HTML characters", () => {
  const result = highlightQuery("<script>alert('xss')</script>", "script");
  expect(result).toContain("&lt;script&gt;");
  expect(result).toContain("alert('xss')");
});