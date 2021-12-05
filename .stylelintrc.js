module.exports = {
  "customSyntax": "postcss-scss",
  "plugins": [
    "stylelint-order",
    "stylelint-z-index-value-constraint"
  ],
  "rules": {
    "at-rule-name-case": "lower",
    "at-rule-name-space-after": "always",
    "at-rule-no-vendor-prefix": true,
    "block-closing-brace-empty-line-before": "never",
    "block-closing-brace-newline-after": "always",
    "block-closing-brace-newline-before": "always-multi-line",
    "block-no-empty": true,
    "block-opening-brace-newline-after": "always-multi-line",
    "block-opening-brace-space-before": "always",
    "comment-no-empty": true,
    "comment-whitespace-inside": "always",
    "declaration-bang-space-after": "never",
    "declaration-bang-space-before": "always",
    "declaration-block-no-duplicate-properties": true,
    "declaration-colon-space-after": "always",
    "declaration-colon-space-before": "never",
    "declaration-no-important": true,
    "declaration-block-no-redundant-longhand-properties": true,
    "declaration-block-no-shorthand-property-overrides": true,
    "declaration-block-semicolon-newline-after": "always-multi-line",
    "declaration-block-semicolon-space-before": "never",
    "declaration-block-single-line-max-declarations": 3,
    "declaration-block-trailing-semicolon": "always",
    "font-weight-notation": "numeric",
    "function-calc-no-unspaced-operator": true,
    "function-comma-newline-before": "never-multi-line",
    "function-comma-space-before": "never",
    "function-linear-gradient-no-nonstandard-direction": true,
    "function-name-case": "lower",
    "function-url-quotes": "always",
    "indentation": 2,
    "max-empty-lines": 1,
    "keyframe-declaration-no-important": true,
    "length-zero-no-unit": true,
    "max-nesting-depth": [
      3,
      {
        "ignore": [
          "blockless-at-rules"
        ],
        "ignoreAtRules": ["media"]
      }
    ],
    "media-feature-colon-space-after": "always",
    "media-feature-colon-space-before": "never",
    "media-feature-name-case": "lower",
    "media-feature-name-no-vendor-prefix": true,
    "media-feature-parentheses-space-inside": "never",
    "media-feature-range-operator-space-after": "always",
    "media-feature-range-operator-space-before": "always",
    "no-duplicate-selectors": true,
    "no-eol-whitespace": true,
    "no-invalid-double-slash-comments": true,
    "no-missing-end-of-source-newline": true,
    "no-unknown-animations": true,
    "number-leading-zero": "always",
    "number-max-precision": 5,
    "number-no-trailing-zeros": true,
    "plugin/z-index-value-constraint": {
      "min": 0,
      "max": 2
    },
    "property-case": "lower",
    "property-no-vendor-prefix": true,
    "selector-attribute-brackets-space-inside": "never",
    "selector-attribute-operator-space-after": "never",
    "selector-attribute-quotes": "always",
    /*
    BEM-ish class regex. From here:
    https://github.com/simonsmith/stylelint-selector-bem-pattern/issues/23#issuecomment-279216443
    */
    "selector-class-pattern": "^(?:(?:o|c|u|t|s|is|has|_|js|qa)-)?[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*(?:__[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*)?(?:--[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*)?(?:\\[.+\\])?$",
    "selector-combinator-space-after": "always",
    "selector-combinator-space-before": "always",
    "selector-descendant-combinator-no-non-space": true,
    "selector-max-id": 0,
    "selector-max-type": 0,
    "selector-max-universal": 0,
    "selector-no-qualifying-type": true,
    "selector-no-vendor-prefix": true,
    "selector-pseudo-class-case": "lower",
    "selector-pseudo-class-parentheses-space-inside": "never",
    "selector-pseudo-element-case": "lower",
    "selector-pseudo-element-colon-notation": "double",
    "selector-type-case": "lower",
    "selector-max-empty-lines": 0,
    "selector-list-comma-space-after": "always-single-line",
    "selector-list-comma-space-before": "never",
    "shorthand-property-no-redundant-values": true,
    "string-no-newline": true,
    "string-quotes": "single",
    "unit-case": "lower",
    "value-no-vendor-prefix": true,
    "value-list-comma-space-after": "always-single-line",
    "value-list-comma-space-before": "never",
    "value-list-max-empty-lines": 0,
    /* At the bottom here because they overwhelm the file otherwise :) */
    "order/order": [
      {
        "type": "at-rule",
        "name": "include"
      },
      "custom-properties",
      "declarations",
      {
        "type": "at-rule",
        "name": "media",
        "hasBlock": true
      },
      "rules"
    ],
    "order/properties-order": [
      {
        "emptyLineBefore": "always",
        "properties": [
          "content"
        ]
      },
      {
        "emptyLineBefore": "always",
        "properties": [
          "position",
          "top",
          "right",
          "bottom",
          "left",
          "z-index"
        ]
      },
      {
        "emptyLineBefore": "always",
        "properties": [
          "align-content",
          "align-items",
          "align-self",
          "flex",
          "flex-basis",
          "flex-direction",
          "flex-flow",
          "flex-grow",
          "flex-shrink",
          "flex-wrap",
          "justify-content",
          "order"
        ]
      },
      {
        "emptyLineBefore": "always",
        "properties": [
          "display",
          "max-width",
          "max-height",
          "min-width",
          "min-height",
          "width",
          "height",
          "clear",
          "float",
          "margin",
          "margin-top",
          "margin-right",
          "margin-bottom",
          "margin-left",
          "padding",
          "padding-top",
          "padding-right",
          "padding-bottom",
          "padding-left",
          "table-layout"
        ]
      },
      {
        "emptyLineBefore": "always",
        "properties": [
          "font-family",
          "font-size",
          "font-style",
          "font-weight",
          "letter-spacing",
          "list-style",
          "list-style-position",
          "line-height",
          "text-align",
          "text-decoration",
          "text-indent",
          "text-overflow",
          "text-rendering",
          "text-transform"
        ]
      },
      {
        "emptyLineBefore": "always",
        "properties": [
          "appearance",
          "background",
          "background-attachment",
          "background-blend-mode",
          "background-color",
          "background-image",
          "background-position",
          "background-repeat",
          "background-size",
          "border",
          "border-color",
          "border-top",
          "border-right",
          "border-bottom",
          "border-left",
          "border-top-color",
          "border-right-color",
          "border-bottom-color",
          "border-left-color",
          "border-radius",
          "border-top-left-radius",
          "border-top-right-radius",
          "border-bottom-right-radius",
          "border-bottom-left-radius",
          "box-shadow",
          "clip",
          "color",
          "cursor",
          "fill",
          "mix-blend-mode",
          "opacity",
          "overflow",
          "overflow-x",
          "overflow-y",
          "visibility",
          "will-change"
        ]
      },
      {
        "emptyLineBefore": "always",
        "properties": [
          "animation",
          "animation-delay",
          "animation-direction",
          "animation-duration",
          "animation-fill-mode",
          "animation-iteration-count",
          "animation-name",
          "animation-play-state",
          "animation-timing-function",
          "transform",
          "transition"
        ]
      }
    ],
    "color-hex-case": "lower",
    "color-hex-length": "short",
    "color-named": [
      "never",
      {
        "ignore": [
          "inside-function"
        ]
      }
    ]
  },
}
