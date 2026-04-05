'use client';
import { Component, type ReactNode } from 'react';

interface Props { children: ReactNode; }
interface State { hasError: boolean; }

export default class ChatErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(error: Error) { console.error('Chat error:', error); }
  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 text-center">
          <p className="text-text-secondary">I encountered an error processing your request. Please try again.</p>
          <button onClick={() => this.setState({ hasError: false })} className="mt-4 text-accent-gold text-sm hover:underline">Dismiss</button>
        </div>
      );
    }
    return this.props.children;
  }
}
