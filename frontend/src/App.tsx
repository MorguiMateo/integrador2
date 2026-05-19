import { Outlet } from 'react-router-dom'
import { Navbar } from './shared/components/Navbar'

export default function App() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
