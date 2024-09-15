import React, { useState } from 'react'
import { motion, useMotionValue, useTransform } from 'framer-motion'
import { Trash2, Send, Clock, CheckCircle, FileText, Plane } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

import React from 'react';
import ReactDOM from 'react-dom/client';
import { ClerkProvider } from '@clerk/clerk-react';
import App from './App';

const clerkFrontendApi = 'your-frontend-api-key';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ClerkProvider frontendApi={clerkFrontendApi}>
      <App />
    </ClerkProvider>
  </React.StrictMode>
);

import React from 'react';
import { SignedIn, SignedOut, SignIn, UserButton } from '@clerk/clerk-react';

function App() {
  return (
    <div>
      {/* When the user is signed in */}
      <SignedIn>
        <h1>Welcome to the Dashboard</h1>
        <UserButton />
      </SignedIn>

      {/* When the user is signed out */}
      <SignedOut>
        <h1>Please Sign In</h1>
        <SignIn />
      </SignedOut>
    </div>
  );
}

export default App;


const emails = [
  { 
    id: 1, 
    subject: "Vehicle Bill of Sale - AI Assisted", 
    sender: "DMV California",
    email: "dmv@california.gov", 
    preview: "Your vehicle sale document is ready for AI-assisted completion...",
    type: "form",
    logo: "/placeholder.svg?height=40&width=40"
  },
  { 
    id: 2, 
    subject: "Delta Flight DL1234 - Check In Now", 
    sender: "Delta Air Lines",
    email: "noreply@delta.com", 
    preview: "Your flight is ready for check-in. Click here for seamless process...",
    type: "flight",
    logo: "/placeholder.svg?height=40&width=40"
  },
  { 
    id: 3, 
    subject: "Team meeting tomorrow", 
    sender: "John Boss",
    email: "boss@company.com", 
    preview: "Let's discuss the new project...",
    type: "regular",
    logo: "/placeholder.svg?height=40&width=40"
  },
  { 
    id: 4, 
    subject: "Your order has shipped", 
    sender: "Amazon",
    email: "orders@amazon.com", 
    preview: "Your recent order #12345 has been shipped...",
    type: "regular",
    logo: "/placeholder.svg?height=40&width=40"
  },
]

export default function Component() {
  const [currentEmail, setCurrentEmail] = useState(0)
  const [lastAction, setLastAction] = useState('')
  const [showFormFilling, setShowFormFilling] = useState(false)
  const [showFlightCheckIn, setShowFlightCheckIn] = useState(false)
  const [signature, setSignature] = useState('')

  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const rotateX = useTransform(y, [-100, 100], [30, -30])
  const rotateY = useTransform(x, [-100, 100], [-30, 30])

  const handleDragEnd = (event, info) => {
    if (info.offset.x < -100) {
      setLastAction('Trashed')
      nextEmail()
    } else if (info.offset.x > 100) {
      setLastAction('Sent')
      nextEmail()
    } else if (info.offset.y > 100) {
      setLastAction('Later')
      nextEmail()
    }
  }

  const nextEmail = () => {
    setCurrentEmail((prev) => (prev + 1) % emails.length)
    setShowFormFilling(false)
    setShowFlightCheckIn(false)
  }

  const handleEmailAction = () => {
    if (emails[currentEmail].type === 'form') {
      setShowFormFilling(true)
    } else if (emails[currentEmail].type === 'flight') {
      setShowFlightCheckIn(true)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="text-2xl font-bold mb-8">Interaction.co</h1>
      {!showFormFilling && !showFlightCheckIn && (
        <motion.div
          style={{
            x,
            y,
            rotateX,
            rotateY,
            cursor: 'grab',
          }}
          drag
          dragConstraints={{ top: 0, right: 0, bottom: 0, left: 0 }}
          dragElastic={0.7}
          onDragEnd={handleDragEnd}
          className="w-96 bg-white p-6 rounded-lg shadow-lg"
        >
          <div className="flex items-center mb-4">
            {/*<img src={emails[currentEmail].logo} alt="Email logo" className="w-10 h-10 mr-3 rounded-full" />*/}
            <div className="w-10 h-10 mr-3 rounded-full bg-black"></div>
            <div>
              <h2 className="text-xl font-semibold">{emails[currentEmail].subject}</h2>
              <p className="text-sm text-gray-600">{emails[currentEmail].sender} &lt;{emails[currentEmail].email}&gt;</p>
            </div>
          </div>
          <p className="text-gray-800 mb-4">{emails[currentEmail].preview}</p>
          {(emails[currentEmail].type === 'form' || emails[currentEmail].type === 'flight') && (
            <Button onClick={handleEmailAction} className="w-full">
              {emails[currentEmail].type === 'form' ? 'Complete Form' : 'Check In'}
            </Button>
          )}
        </motion.div>
      )}
      {showFormFilling && (
        <Card className="w-96">
          <CardHeader>
            <CardTitle>AI-Assisted Form Filling</CardTitle>
          </CardHeader>
          <CardContent>
            <img src="/placeholder.svg?height=300&width=400" alt="Bill of Sale Form" className="w-full mb-4 rounded-lg shadow" />
            <p className="mb-4">The AI has analyzed the attached Bill of Sale form and pre-filled it with the following information:</p>
            <ul className="list-disc pl-5 mb-4">
              <li>Vehicle ID: 1HGBH41JXMN109186</li>
              <li>Seller: John Doe</li>
              <li>Buyer: Jane Smith</li>
              <li>Sale Date: {new Date().toLocaleDateString()}</li>
              <li>Sale Price: $15,000</li>
            </ul>
            <div className="mb-4">
              <label htmlFor="signature" className="block text-sm font-medium text-gray-700 mb-1">
                Signature:
              </label>
              <Input
                type="text"
                id="signature"
                placeholder="Type your name to sign"
                value={signature}
                onChange={(e) => setSignature(e.target.value)}
                className="w-full p-2 border rounded"
              />
            </div>
            <div className="flex justify-between">
              <Button onClick={() => setShowFormFilling(false)} className="mr-2">Confirm & Send</Button>
              <Button variant="outline" onClick={() => setShowFormFilling(false)}>Edit</Button>
            </div>
          </CardContent>
        </Card>
      )}
      {showFlightCheckIn && (
        <Card className="w-96">
          <CardHeader className="flex items-center">
            <img src="/placeholder.svg?height=40&width=40" alt="Delta logo" className="w-10 h-10 mr-3" />
            <CardTitle>Delta Flight Check-In</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">You're checked in for your flight DL1234!</p>
            <ul className="list-disc pl-5 mb-4">
              <li>Departure: New York (JFK) at 10:00 AM</li>
              <li>Arrival: Los Angeles (LAX) at 1:30 PM</li>
              <li>Seat: 14A (Window)</li>
            </ul>
            <div className="flex justify-between">
              <Button onClick={() => setShowFlightCheckIn(false)} className="mr-2">
                <CheckCircle className="mr-2 h-4 w-4" /> Confirmed
              </Button>
              <Button variant="outline" onClick={() => setShowFlightCheckIn(false)}>
                <FileText className="mr-2 h-4 w-4" /> Boarding Pass
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
      {!showFormFilling && !showFlightCheckIn && (
        <div className="mt-8 flex justify-center space-x-8">
          <div className="flex flex-col items-center">
            <Trash2 className="text-black" />
            <span className="text-sm mt-1">Trash</span>
          </div>
          <div className="flex flex-col items-center">
            <Send className="text-black" />
            <span className="text-sm mt-1">Send</span>
          </div>
          <div className="flex flex-col items-center">
            <Clock className="text-black" />
            <span className="text-sm mt-1">Later</span>
          </div>
        </div>
      )}
      {lastAction && (
        <div className="mt-4 text-lg font-semibold">
          Last action: {lastAction}
        </div>
      )}
    </div>
  )
}
