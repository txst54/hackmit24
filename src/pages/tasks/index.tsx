import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function Component() {
    const agents = [
        {
            name: "CodeReviewBot",
            task: "PR Code Review",
            description: "Analyzes pull requests, provides code suggestions, and checks for best practices."
        },
        {
            name: "CalendarAssistant",
            task: "Adding Tasks to Calendar",
            description: "Scans emails for event details and automatically adds them to the user's calendar."
        },
        {
            name: "FormFiller",
            task: "Fill Out Forms",
            description: "Extracts relevant information from emails to auto-fill online forms and documents."
        },
        {
            name: "MeetingScheduler",
            task: "Adding Tasks to Calendar",
            description: "Coordinates with multiple parties to find suitable meeting times and schedules them."
        },
        {
            name: "SecurityReviewer",
            task: "PR Code Review",
            description: "Focuses on identifying potential security vulnerabilities in code changes."
        }
    ]

    return (
        <div className="container mx-auto py-10">
            <Table>
                <TableCaption>Table of Email Automation Agents</TableCaption>
                <TableHeader>
                    <TableRow>
                        <TableHead className="w-[200px]">Agent Name</TableHead>
                        <TableHead>Primary Task</TableHead>
                        <TableHead className="hidden md:table-cell">Description</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {agents.map((agent, index) => (
                        <TableRow key={index}>
                            <TableCell className="font-medium">{agent.name}</TableCell>
                            <TableCell>{agent.task}</TableCell>
                            <TableCell className="hidden md:table-cell">{agent.description}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}