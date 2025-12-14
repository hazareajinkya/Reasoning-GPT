"use client";

import { useState, useEffect } from "react";

export default function ConnectionCheck() {
  const [backendStatus, setBackendStatus] = useState<"checking" | "connected" | "disconnected">("checking");
  const [backendInfo, setBackendInfo] = useState<any>(null);

  useEffect(() => {
    const checkBackend = async () => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
      
      try {
        const response = await fetch("http://localhost:8000/health", {
          method: "GET",
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
          const data = await response.json();
          setBackendInfo(data);
          setBackendStatus("connected");
        } else {
          setBackendStatus("disconnected");
        }
      } catch (err) {
        clearTimeout(timeoutId);
        setBackendStatus("disconnected");
      }
    };

    checkBackend();
    // Check every 10 seconds
    const interval = setInterval(checkBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  if (backendStatus === "checking") {
    return (
      <div className="bg-yellow-900 border border-yellow-700 text-yellow-200 px-4 py-2 rounded-lg text-sm">
        🔄 Checking backend connection...
      </div>
    );
  }

  if (backendStatus === "disconnected") {
    return (
      <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-2 rounded-lg text-sm">
        <strong>⚠️ Backend Disconnected</strong>
        <p className="mt-1 text-xs">
          Make sure the backend is running: <code className="bg-red-800 px-1 rounded">./start_backend.sh</code>
        </p>
      </div>
    );
  }

  if (backendInfo && backendInfo.items === 0) {
    return (
      <div className="bg-yellow-900 border border-yellow-700 text-yellow-200 px-4 py-2 rounded-lg text-sm">
        <strong>⚠️ Backend Connected but No Data</strong>
        <p className="mt-1 text-xs">
          Vector store not loaded. Restart the backend to load the vector store.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-green-900 border border-green-700 text-green-200 px-4 py-2 rounded-lg text-sm">
      ✅ Backend Connected ({backendInfo?.items || 0} problems loaded)
    </div>
  );
}

