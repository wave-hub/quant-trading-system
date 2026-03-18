import React, { useRef } from 'react';
import Editor, { useMonaco } from '@monaco-editor/react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string | undefined) => void;
  language?: string;
  height?: string | number;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ value, onChange, language = 'python', height = '500px' }) => {
  const monaco = useMonaco();
  const editorRef = useRef<any>(null);

  const handleEditorDidMount = (editor: any, m: any) => {
    editorRef.current = editor;
    
    // 自定义一些 Python 量化提示词 (可选)
    m.languages.registerCompletionItemProvider('python', {
      provideCompletionItems: (model: any, position: any) => {
        const word = model.getWordUntilPosition(position);
        const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn
        };
        const suggestions = [
            {
                label: 'on_bar',
                kind: m.languages.CompletionItemKind.Function,
                insertText: 'def on_bar(context, bar):\n    pass',
                range: range
            },
            {
                label: 'on_tick',
                kind: m.languages.CompletionItemKind.Function,
                insertText: 'def on_tick(context, tick):\n    pass',
                range: range
            }
        ];
        return { suggestions: suggestions };
      }
    });
  };

  return (
    <div style={{ border: '1px solid #d9d9d9', borderRadius: '6px', overflow: 'hidden' }}>
      <Editor
        height={height}
        language={language}
        theme="vs-dark"
        value={value}
        onChange={onChange}
        onMount={handleEditorDidMount}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          wordWrap: 'on',
          scrollBeyondLastLine: false,
          smoothScrolling: true,
          cursorBlinking: 'smooth',
        }}
      />
    </div>
  );
};

export default CodeEditor;
