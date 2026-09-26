/*
ABOUTME: Route for creating a new gift.
ABOUTME: Renders the GiftForm component for user input.
*/

import { createFileRoute } from "@tanstack/react-router"

import GiftForm from "@/components/Items/GiftForm"

export const Route = createFileRoute("/create-gift")({
  component: CreateGift,
})

function CreateGift() {
  return (
    <div className="container relative hidden h-[800px] flex-col items-center justify-center md:grid lg:max-w-none lg:grid-cols-1 lg:px-0">
      <div className="lg:p-8">
        <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
          <div className="flex flex-col space-y-2 text-center">
            <h1 className="text-2xl font-semibold tracking-tight">
              Create a new gift
            </h1>
            <p className="text-sm text-muted-foreground">
              Enter the details for your new gift
            </p>
          </div>
          <GiftForm />
        </div>
      </div>
    </div>
  )
}
