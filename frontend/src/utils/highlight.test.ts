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

  test("returns original text when query is empty", () => {
    const result = highlightQuery("Some text", "");
    expect(result).toBe("Some text");
  });

  test("escapes HTML characters", () => {
    const result = highlightQuery("<script>alert('xss')</script>", "script");
    expect(result).toContain("&lt;");
    expect(result).toContain("&gt;");
    expect(result).toContain('<mark class="highlight">script</mark>');
    expect(result).toContain("alert('xss')");
    expect(result).toBe(
      '&lt;<mark class="highlight">script</mark>&gt;alert(\'xss\')&lt;/<mark class="highlight">script</mark>&gt;'
    );
  });

  test("handles special regex characters in query", () => {
    const result = highlightQuery("test (with) special [chars]", "(with)");
    expect(result).toContain('<mark class="highlight">(with)</mark>');
  });

  test("handles multiple spaces in query", () => {
    const result = highlightQuery("Python Java C++", "python  java");
    expect(result).toContain('<mark class="highlight">Python</mark>');
    expect(result).toContain('<mark class="highlight">Java</mark>');
    expect(result).not.toContain('<mark class="highlight">C++</mark>');
  });
});

describe("getStatusLabel", () => {
  test("returns localized labels", () => {
    expect(getStatusLabel("ready")).toBe("Готово");
    expect(getStatusLabel("indexing")).toBe("Индексация...");
    expect(getStatusLabel("uploading")).toBe("Загрузка...");
    expect(getStatusLabel("failed")).toBe("Ошибка");
    expect(getStatusLabel("unknown")).toBe("unknown");
  });
});
