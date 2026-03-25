import type { editor } from "monaco-editor";

export const BLUE_LIGHT_THEME_NAME = "blueLight";

export const blueLightTheme: editor.IStandaloneThemeData = {
	base: "vs",
	inherit: true,

	rules: [
		{ token: "", foreground: "1e293b" },
		{
			token: "comment",
			foreground: "94a3b8",
			fontStyle: "italic",
		},
		{
			token: "comment.line",
			foreground: "94a3b8",
			fontStyle: "italic",
		},

		{ token: "string", foreground: "059669" },
		{ token: "string.single", foreground: "059669" },
		{ token: "string.double", foreground: "059669" },
		{ token: "string.template", foreground: "059669" },
		{ token: "string.regexp", foreground: "0d9488" },

		{ token: "number", foreground: "d97706" },
		{ token: "number.hex", foreground: "d97706" },
		{ token: "number.float", foreground: "d97706" },
		{ token: "constant", foreground: "7c3aed" },
		{
			token: "constant.language",
			foreground: "7c3aed",
			fontStyle: "bold",
		},
		{ token: "constant.numeric", foreground: "d97706" },
		{
			token: "constant.boolean",
			foreground: "7c3aed",
			fontStyle: "bold",
		},

		{
			token: "keyword",
			foreground: "1d4ed8",
			fontStyle: "bold",
		},
		{
			token: "keyword.control",
			foreground: "1d4ed8",
			fontStyle: "bold",
		},
		{ token: "keyword.operator", foreground: "475569" },
		{
			token: "keyword.declaration",
			foreground: "1d4ed8",
			fontStyle: "bold",
		},

		{ token: "type", foreground: "0891b2" },
		{
			token: "type.class",
			foreground: "0891b2",
			fontStyle: "bold",
		},
		{
			token: "type.interface",
			foreground: "0891b2",
			fontStyle: "bold",
		},
		{ token: "type.enum", foreground: "0891b2" },

		{ token: "function", foreground: "7c3aed" },
		{ token: "function.method", foreground: "7c3aed" },
		{ token: "function.constructor", foreground: "7c3aed" },

		{ token: "variable", foreground: "1e293b" },
		{ token: "variable.parameter", foreground: "ea580c" },
		{ token: "variable.property", foreground: "1e293b" },
		{ token: "variable.other", foreground: "1e293b" },

		{ token: "operator", foreground: "475569" },
		{ token: "delimiter", foreground: "475569" },
		{ token: "delimiter.bracket", foreground: "64748b" },
		{ token: "delimiter.parenthesis", foreground: "64748b" },
		{ token: "delimiter.brace", foreground: "64748b" },

		{ token: "tag", foreground: "1d4ed8" },
		{ token: "tag.name", foreground: "1d4ed8" },
		{ token: "tag.attribute", foreground: "0891b2" },
		{ token: "tag.delimiter", foreground: "64748b" },

		{ token: "annotation", foreground: "7c3aed" },
		{ token: "decorator", foreground: "7c3aed" },

		{
			token: "invalid",
			foreground: "dc2626",
			fontStyle: "underline",
		},
		{
			token: "invalid.illegal",
			foreground: "dc2626",
			fontStyle: "bold underline",
		},
	],

	colors: {
		"editor.background": "#c6e3ff",
		"editor.foreground": "#1e293b",

		"editorCursor.foreground": "#1d4ed8",
		"editorCursor.background": "#ffffff",
		"editor.selectionBackground": "#0080ffb5",
		"editor.selectionHighlightBackground": "#24272a40",
		"editor.inactiveSelectionBackground": "#3a3e4130",

		"editor.lineHighlightBackground": "#c6e3ff40",
		"editor.lineHighlightBorder": "#c6e3ff00",
		"editor.wordHighlightBackground": "#c6e3ff60",
		"editor.wordHighlightStrongBackground": "#93c5fd80",

		"editorLineNumber.foreground": "#94a3b8",
		"editorLineNumber.background": "#c6e3ff",
		"editorLineNumber.activeForeground": "#475569",

		"editorBracketMatch.background": "#c6e3ff60",
		"editorBracketMatch.border": "#93c5fd",
		"editorBracketHighlight.foreground1": "#1d4ed8",
		"editorBracketHighlight.foreground2": "#0891b2",
		"editorBracketHighlight.foreground3": "#7c3aed",

		"editor.findMatchBackground": "#fcd34d80",
		"editor.findMatchHighlightBackground": "#fde68a80",
		"editor.findRangeHighlightBackground": "#c6e3ff40",

		"editorError.foreground": "#dc2626",
		"editorError.border": "#dc262600",
		"editorWarning.foreground": "#d97706",
		"editorInfo.foreground": "#0891b2",
		"editorHint.foreground": "#64748b",

		"editorGutter.background": "#ffffff",
		"editorGutter.addedBackground": "#22c55e",
		"editorGutter.modifiedBackground": "#3b82f6",
		"editorGutter.deletedBackground": "#ef4444",

		"scrollbarSlider.background": "#94a3b840",
		"scrollbarSlider.hoverBackground": "#94a3b880",
		"scrollbarSlider.activeBackground": "#64748b80",

		"editorWidget.background": "#f8fafc",
		"editorWidget.border": "#cbd5e1",
		"editorSuggestWidget.background": "#f8fafc",
		"editorSuggestWidget.border": "#cbd5e1",
		"editorSuggestWidget.highlightForeground": "#1d4ed8",
		"editorHoverWidget.background": "#ffffff",
		"editorHoverWidget.border": "#cbd5e1",

		"peekView.border": "#93c5fd",
		"peekViewEditor.background": "#f8fafc",
		"peekViewResult.background": "#f1f5f9",
		"peekViewResult.selectionBackground": "#c6e3ff80",

		"diffEditor.insertedTextBackground": "#22c55e20",
		"diffEditor.removedTextBackground": "#ef444420",
	},
};
