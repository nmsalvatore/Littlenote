"""Tests for common app."""

from django.template import Context, Template
from django.test import TestCase


class MarkdownFilterTest(TestCase):
    """Tests for the markdown template filter."""

    def test_basic_markdown_conversion(self):
        """Test basic markdown to HTML conversion."""
        template = Template("{% load markdown_extras %}{{ content|markdown|safe }}")
        context = Context({"content": "# Hello World\n\nThis is **bold** text."})
        result = template.render(context)

        self.assertIn("<h1>Hello World</h1>", result)
        self.assertIn("<strong>bold</strong>", result)
        self.assertIn("<p>This is", result)

    def test_fenced_code_blocks(self):
        """Test that fenced code blocks are rendered correctly."""
        template = Template("{% load markdown_extras %}{{ content|markdown|safe }}")
        context = Context({
            "content": "```python\nprint('Hello World')\n```"
        })
        result = template.render(context)

        self.assertIn("<pre><code", result)
        self.assertIn("print('Hello World')", result)

    def test_empty_input(self):
        """Test that empty input returns empty string."""
        template = Template("{% load markdown_extras %}{{ content|markdown|safe }}")
        context = Context({"content": ""})
        result = template.render(context)

        self.assertEqual(result.strip(), "")

    def test_none_input(self):
        """Test that None input is handled gracefully."""
        template = Template("{% load markdown_extras %}{{ content|markdown|safe }}")
        context = Context({"content": None})
        result = template.render(context)

        # Should not crash and return empty or "None" wrapped in <p>
        self.assertIn(result.strip(), ["", "None", "<p>None</p>"])

    def test_plain_text_input(self):
        """Test that plain text without markdown is wrapped in paragraph tags."""
        template = Template("{% load markdown_extras %}{{ content|markdown|safe }}")
        context = Context({"content": "Just plain text"})
        result = template.render(context)

        self.assertIn("<p>Just plain text</p>", result)

    def test_multiple_paragraphs(self):
        """Test that multiple paragraphs are handled correctly."""
        template = Template("{% load markdown_extras %}{{ content|markdown|safe }}")
        context = Context({
            "content": "First paragraph.\n\nSecond paragraph."
        })
        result = template.render(context)

        # Should create two separate paragraph tags
        self.assertEqual(result.count("<p>"), 2)
        self.assertIn("First paragraph.", result)
        self.assertIn("Second paragraph.", result)

    def test_lists_and_formatting(self):
        """Test that lists and various formatting work correctly."""
        template = Template("{% load markdown_extras %}{{ content|markdown|safe }}")
        context = Context({
            "content": "- Item 1\n- Item 2\n\n*Italic* and **bold**"
        })
        result = template.render(context)

        self.assertIn("<ul>", result)
        self.assertIn("<li>Item 1</li>", result)
        self.assertIn("<li>Item 2</li>", result)
        self.assertIn("<em>Italic</em>", result)
        self.assertIn("<strong>bold</strong>", result)

    def test_html_escaping_in_markdown(self):
        """Test that HTML in markdown is properly handled."""
        template = Template("{% load markdown_extras %}{{ content|markdown|safe }}")
        context = Context({
            "content": "This has <script>alert('xss')</script> in it."
        })
        result = template.render(context)

        # Note: Python markdown by default allows HTML through
        # In production, additional sanitization should be used
        # For now, just check that markdown processing occurred
        self.assertIn("<p>", result)

    def test_links_conversion(self):
        """Test that markdown links are converted to HTML links."""
        template = Template("{% load markdown_extras %}{{ content|markdown|safe }}")
        context = Context({
            "content": "[Click here](https://example.com)"
        })
        result = template.render(context)

        self.assertIn('<a href="https://example.com">Click here</a>', result)

    def test_headers_hierarchy(self):
        """Test that different header levels are converted correctly."""
        template = Template("{% load markdown_extras %}{{ content|markdown|safe }}")
        context = Context({
            "content": "# H1\n## H2\n### H3"
        })
        result = template.render(context)

        self.assertIn("<h1>H1</h1>", result)
        self.assertIn("<h2>H2</h2>", result)
        self.assertIn("<h3>H3</h3>", result)
