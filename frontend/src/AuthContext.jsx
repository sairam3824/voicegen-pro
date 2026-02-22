import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();
const API_BASE = 'http://localhost:8000';

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem("token"));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            fetchUser();
        } else {
            setLoading(false);
        }
    }, [token]);

    const fetchUser = async () => {
        try {
            const response = await fetch(`${API_BASE}/users/me`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (response.ok) {
                const data = await response.json();
                setUser(data);
            } else {
                logout();
            }
        } catch (error) {
            console.error("Failed to fetch user:", error);
            logout();
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const response = await fetch(`${API_BASE}/token`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Login failed");
        }

        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        setToken(data.access_token);
        // User will be fetched by useEffect
    };

    const register = async (email, password) => {
        const response = await fetch(`${API_BASE}/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Registration failed");
        }

        // Auto login after register
        const data = await response.json();
        localStorage.setItem("token", data.access_token);
        setToken(data.access_token);
    }

    const logout = () => {
        localStorage.removeItem("token");
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
