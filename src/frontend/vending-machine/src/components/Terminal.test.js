import { render, screen, fireEvent } from '@testing-library/react';
import Terminal from './Terminal';

describe('Terminal Component', () => {
  test('renders terminal prompt', () => {
    render(<Terminal />);
    const prompt = screen.getByText(/T17-Vend:~\$/i);
    expect(prompt).toBeInTheDocument();
  });

  test('accepts user input and displays it', () => {
    render(<Terminal />);
    const input = screen.getByRole('textbox');

    fireEvent.change(input, { target: { value: 'list' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    const echoed = screen.getByText(/list/i);
    expect(echoed).toBeInTheDocument();
  });

  test('handles unknown command gracefully', () => {
    render(<Terminal />);
    const input = screen.getByRole('textbox');

    fireEvent.change(input, { target: { value: 'foobar' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    const errorMsg = screen.getByText(/Unknown command/i);
    expect(errorMsg).toBeInTheDocument();
  });
});