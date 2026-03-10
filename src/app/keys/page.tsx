"use client"

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  ChevronLeft, 
  Key, 
  Plus, 
  Copy, 
  Trash2,
  Lock,
  Eye,
  CheckCircle2
} from "lucide-react";
import Link from 'next/link';

interface ApiKey {
  id: number;
  name: string;
  created_at: string;
}

export default function ApiKeysPortal() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [newKeyData, setNewKeyData] = useState<{name: string, key: string} | null>(null);

  const fetchKeys = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/keys', {
        headers: { 'X-Nexus-Key': 'development_key' }
      });
      if (response.ok) {
        setKeys(await response.json());
      }
    } catch (error) {
      console.error("Failed to fetch keys:", error);
    } finally {
      setLoading(false);
    }
  };

  const generateKey = async () => {
    const name = prompt("Enter a name for this key (e.g., 'Claude-3.7-Work'):");
    if (!name) return;

    try {
      const response = await fetch(`/api/v1/keys/generate?name=${encodeURIComponent(name)}`, {
        method: 'POST',
        headers: { 'X-Nexus-Key': 'development_key' }
      });
      if (response.ok) {
        const data = await response.json();
        setNewKeyData(data);
        fetchKeys();
      }
    } catch (error) {
      console.error("Failed to generate key:", error);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 p-6 font-sans">
      <header className="flex justify-between items-center mb-10 border-b border-neutral-800 pb-6">
        <div className="flex items-center gap-3">
          <Link href="/">
            <Button variant="ghost" size="icon" className="text-neutral-400 hover:text-white">
              <ChevronLeft className="h-6 w-6" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">API KEYS</h1>
            <p className="text-sm text-neutral-400">Secure access management for your agent mesh</p>
          </div>
        </div>
        <Button onClick={generateKey} className="bg-blue-600 hover:bg-blue-700">
          <Plus className="mr-2 h-4 w-4" /> Generate New Key
        </Button>
      </header>

      <main className="max-w-4xl mx-auto space-y-8">
        {newKeyData && (
          <Card className="bg-blue-900/10 border-blue-500/50 border-dashed animate-in fade-in slide-in-from-top-4 duration-500">
            <CardHeader>
              <CardTitle className="text-blue-400 flex items-center gap-2 italic">
                <CheckCircle2 className="h-5 w-5" /> New Key Generated Successfully
              </CardTitle>
              <CardDescription className="text-blue-300/70">
                Copy this key now. For security reasons, you won't be able to see it again.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 bg-black/40 p-3 rounded border border-blue-900/30">
                <code className="text-blue-400 font-mono text-sm flex-1">{newKeyData.key}</code>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => {
                    navigator.clipboard.writeText(newKeyData.key);
                    alert("Key copied to clipboard!");
                  }}
                  className="hover:bg-blue-900/20 text-blue-400"
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setNewKeyData(null)}
                className="mt-4 text-[10px] uppercase tracking-widest text-neutral-500 hover:text-white"
              >
                Done
              </Button>
            </CardContent>
          </Card>
        )}

        <Card className="bg-neutral-900/50 border-neutral-800 backdrop-blur-md">
          <CardHeader>
            <CardTitle className="text-lg">Active Mesh Keys</CardTitle>
            <CardDescription className="text-neutral-500 font-mono text-xs">
              Keys provide authenticated access to the Nexus Mission API.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="py-10 text-center text-neutral-500 italic">Decrypting key-vault...</div>
            ) : keys.length === 0 ? (
              <div className="py-10 text-center text-neutral-500">No active keys. Create one to begin external agent integration.</div>
            ) : (
              <div className="space-y-4">
                {keys.map((key) => (
                  <div key={key.id} className="flex items-center justify-between p-4 bg-neutral-900 border border-neutral-800 rounded-lg hover:border-neutral-700 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-8 h-8 bg-neutral-800 rounded flex items-center justify-center">
                        <Key className="text-neutral-500 w-4 h-4" />
                      </div>
                      <div>
                        <h4 className="font-medium text-sm">{key.name}</h4>
                        <p className="text-[10px] text-neutral-500 font-mono">
                          CREATED: {new Date(key.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                       <span className="text-[10px] font-mono bg-neutral-800 px-2 py-1 rounded text-neutral-400">
                          nx_••••••••••••••••
                       </span>
                       <Button variant="ghost" size="icon" className="text-neutral-600 hover:text-red-400 hover:bg-neutral-800">
                          <Trash2 className="h-4 w-4" />
                       </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Security Notice */}
        <div className="flex items-start gap-3 p-4 bg-yellow-900/10 border border-yellow-900/30 rounded-lg">
          <Lock className="text-yellow-600 h-5 w-5 mt-0.5" />
          <div>
            <h5 className="text-sm font-semibold text-yellow-600 uppercase tracking-tight">Security Protocol</h5>
            <p className="text-xs text-neutral-400 mt-1 leading-relaxed">
              API keys grant full access to your mission orchestration engine. Never share your keys or commit them to public repositories. All requests are logged in the Nexus Audit Mesh.
            </p>
          </div>
        </div>
      </main>

      <footer className="mt-20 text-center text-neutral-700 text-[10px] font-mono border-t border-neutral-900 pt-8">
        N\u00dcMTEMA SECURE VAULT v4.1 \u2022 SHA-256 HASHING ACTIVE \u2022 PROPRIETARY
      </footer>
    </div>
  );
}
