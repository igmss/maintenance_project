import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import App from '../App';
import { AuthProvider } from '../lib/auth';

// Mock the API client
vi.mock('../lib/api', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    setToken: vi.fn(),
  },
}));

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('App Component', () => {
  beforeEach(() => {
    // Clear local storage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  test('renders landing page by default', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should show the landing page elements
    expect(screen.getByText(/maintenance platform/i)).toBeInTheDocument();
    expect(screen.getByText(/find trusted service providers/i)).toBeInTheDocument();
  });

  test('shows login page when clicking login button', async () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Click login button
    const loginButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(loginButton);

    // Should navigate to login page
    await waitFor(() => {
      expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument();
    });
  });

  test('shows registration page when clicking register button', async () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Click register button
    const registerButton = screen.getByRole('button', { name: /get started/i });
    fireEvent.click(registerButton);

    // Should navigate to registration page
    await waitFor(() => {
      expect(screen.getByText(/create your account/i)).toBeInTheDocument();
    });
  });

  test('redirects to login when accessing protected routes without authentication', () => {
    // Mock window.location
    delete window.location;
    window.location = { pathname: '/dashboard' };

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should redirect to login
    expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument();
  });
});

describe('Authentication Flow', () => {
  test('successful login redirects to appropriate dashboard', async () => {
    const mockApiResponse = {
      success: true,
      user: {
        id: 1,
        email: 'customer@example.com',
        user_type: 'customer',
        full_name: 'Test Customer'
      },
      token: 'mock-jwt-token'
    };

    // Mock successful login API call
    const { apiClient } = await import('../lib/api');
    apiClient.post.mockResolvedValueOnce({ data: mockApiResponse });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Navigate to login page
    const loginButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument();
    });

    // Fill in login form
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: 'customer@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    // Should redirect to customer dashboard
    await waitFor(() => {
      expect(screen.getByText(/customer dashboard/i)).toBeInTheDocument();
    });
  });

  test('failed login shows error message', async () => {
    const mockApiError = {
      response: {
        data: {
          success: false,
          error: 'Invalid credentials'
        }
      }
    };

    // Mock failed login API call
    const { apiClient } = await import('../lib/api');
    apiClient.post.mockRejectedValueOnce(mockApiError);

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Navigate to login page and submit invalid credentials
    const loginButton = screen.getByRole('button', { name: /sign in/i });
    fireEvent.click(loginButton);

    await waitFor(() => {
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
      fireEvent.click(submitButton);
    });

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});

describe('Service Booking Flow', () => {
  beforeEach(() => {
    // Mock authenticated user
    localStorage.setItem('token', 'mock-jwt-token');
    localStorage.setItem('user', JSON.stringify({
      id: 1,
      email: 'customer@example.com',
      user_type: 'customer',
      full_name: 'Test Customer'
    }));
  });

  test('customer can browse service categories', async () => {
    const mockServices = {
      success: true,
      categories: [
        {
          id: 1,
          name_en: 'Plumbing',
          name_ar: 'السباكة',
          description_en: 'Plumbing services',
          icon: 'plumbing-icon'
        },
        {
          id: 2,
          name_en: 'Electrical',
          name_ar: 'الكهرباء',
          description_en: 'Electrical services',
          icon: 'electrical-icon'
        }
      ]
    };

    const { apiClient } = await import('../lib/api');
    apiClient.get.mockResolvedValueOnce({ data: mockServices });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should show service categories
    await waitFor(() => {
      expect(screen.getByText(/plumbing/i)).toBeInTheDocument();
      expect(screen.getByText(/electrical/i)).toBeInTheDocument();
    });
  });

  test('customer can create a booking', async () => {
    const mockBookingResponse = {
      success: true,
      booking: {
        id: 1,
        service_category_id: 1,
        description: 'Fix leaking faucet',
        status: 'pending',
        preferred_date: '2024-08-06',
        preferred_time: '10:00'
      }
    };

    const { apiClient } = await import('../lib/api');
    apiClient.post.mockResolvedValueOnce({ data: mockBookingResponse });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Navigate to booking page
    const bookServiceButton = screen.getByRole('button', { name: /book service/i });
    fireEvent.click(bookServiceButton);

    await waitFor(() => {
      // Fill in booking form
      const descriptionInput = screen.getByLabelText(/description/i);
      const dateInput = screen.getByLabelText(/preferred date/i);
      const submitButton = screen.getByRole('button', { name: /book now/i });

      fireEvent.change(descriptionInput, { target: { value: 'Fix leaking faucet' } });
      fireEvent.change(dateInput, { target: { value: '2024-08-06' } });
      fireEvent.click(submitButton);
    });

    // Should show booking confirmation
    await waitFor(() => {
      expect(screen.getByText(/booking created successfully/i)).toBeInTheDocument();
    });
  });
});

describe('Language Switching', () => {
  test('switches between English and Arabic', async () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should start in English
    expect(screen.getByText(/maintenance platform/i)).toBeInTheDocument();

    // Click language switcher
    const languageButton = screen.getByRole('button', { name: /language/i });
    fireEvent.click(languageButton);

    // Select Arabic
    const arabicOption = screen.getByText(/العربية/);
    fireEvent.click(arabicOption);

    // Should switch to Arabic
    await waitFor(() => {
      expect(screen.getByText(/منصة الصيانة/)).toBeInTheDocument();
    });
  });

  test('persists language preference', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Change language
    const languageButton = screen.getByRole('button', { name: /language/i });
    fireEvent.click(languageButton);
    
    const arabicOption = screen.getByText(/العربية/);
    fireEvent.click(arabicOption);

    // Language preference should be saved
    expect(localStorage.getItem('language')).toBe('ar');
  });
});

describe('Responsive Design', () => {
  test('adapts to mobile viewport', () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should show mobile navigation
    const mobileMenuButton = screen.getByRole('button', { name: /menu/i });
    expect(mobileMenuButton).toBeInTheDocument();
  });

  test('shows desktop navigation on larger screens', () => {
    // Mock desktop viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should show desktop navigation
    expect(screen.getByText(/services/i)).toBeInTheDocument();
    expect(screen.getByText(/about/i)).toBeInTheDocument();
  });
});

describe('Error Handling', () => {
  test('shows error boundary for JavaScript errors', () => {
    // Mock console.error to avoid noise in test output
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Component that throws an error
    const ThrowError = () => {
      throw new Error('Test error');
    };

    render(
      <TestWrapper>
        <ThrowError />
      </TestWrapper>
    );

    // Should show error boundary
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();

    consoleSpy.mockRestore();
  });

  test('handles network errors gracefully', async () => {
    const { apiClient } = await import('../lib/api');
    apiClient.get.mockRejectedValueOnce(new Error('Network error'));

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Should show network error message
    await waitFor(() => {
      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });
  });
});

describe('Accessibility', () => {
  test('has proper ARIA labels', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Check for ARIA labels
    expect(screen.getByRole('main')).toBeInTheDocument();
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByLabelText(/search services/i)).toBeInTheDocument();
  });

  test('supports keyboard navigation', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Tab through interactive elements
    const firstButton = screen.getByRole('button', { name: /sign in/i });
    firstButton.focus();
    expect(document.activeElement).toBe(firstButton);

    // Press Tab to move to next element
    fireEvent.keyDown(firstButton, { key: 'Tab' });
    // Next focusable element should be focused
  });

  test('has proper heading hierarchy', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Check heading hierarchy
    const h1 = screen.getByRole('heading', { level: 1 });
    expect(h1).toBeInTheDocument();
    expect(h1).toHaveTextContent(/maintenance platform/i);
  });
});

