/*
ABOUTME: Route for creating a new gift.
ABOUTME: Renders the GiftForm component for user input.
*/

import { Container, Heading } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import GiftForm from "@/components/Items/GiftForm"

export const Route = createFileRoute("/_layout/create-gift")({
  component: CreateGift,
})

function CreateGift() {
  return (
    <Container maxW="sm">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        Create a new gift
      </Heading>

      <GiftForm />
    </Container>
  )
}
