/*
ABOUTME: Form component for creating and updating gifts.
ABOUTME: Utilizes Shadcn UI components and react-hook-form for validation.
*/

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  Button,
  Input,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"

import { type GiftCreate, GiftsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { Field } from "../ui/field"

const GiftForm = () => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<GiftCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      approximate_price: 0,
      description: "",
      product_link: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: GiftCreate) => {
      const formData = new FormData()
      formData.append("name", data.name)
      formData.append("approximate_price", data.approximate_price.toString())
      if (data.description) formData.append("description", data.description)
      if (data.product_link) formData.append("product_link", data.product_link)
      if (data.photo) formData.append("photo", data.photo)
      return GiftsService.createGift({ formData: formData })
    },
    onSuccess: () => {
      showSuccessToast("Gift created successfully.")
      reset()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["gifts"] })
    },
  })

  const onSubmit: SubmitHandler<GiftCreate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <VStack gap={4}>
        <Field
          required
          invalid={!!errors.name}
          errorText={errors.name?.message}
          label="Name"
        >
          <Input
            id="name"
            {...register("name", {
              required: "Name is required.",
            })}
            placeholder="Gift Name"
            type="text"
          />
        </Field>

        <Field
          required
          invalid={!!errors.approximate_price}
          errorText={errors.approximate_price?.message}
          label="Approximate Price"
        >
          <Input
            id="approximate_price"
            {...register("approximate_price", {
              required: "Approximate Price is required.",
              valueAsNumber: true,
              min: { value: 0, message: "Price must be positive." },
            })}
            placeholder="0.00"
            type="number"
            step="0.01"
          />
        </Field>

        <Field
          invalid={!!errors.description}
          errorText={errors.description?.message}
          label="Description"
        >
          <Textarea
            id="description"
            {...register("description")}
            placeholder="A brief description of the gift"
          />
        </Field>

        <Field
          invalid={!!errors.product_link}
          errorText={errors.product_link?.message}
          label="Product Link"
        >
          <Input
            id="product_link"
            {...register("product_link")}
            placeholder="https://example.com/product"
            type="url"
          />
        </Field>

        <Field
          invalid={!!errors.photo}
          errorText={errors.photo?.message}
          label="Gift Image"
        >
          <Input
            id="photo"
            {...register("photo")}
            type="file"
            accept="image/*"
          />
        </Field>
      </VStack>

      <Button
        type="submit"
        disabled={!isValid || isSubmitting}
        loading={isSubmitting}
        className="w-full"
      >
        Create Gift
      </Button>
    </form>
  )
}

export default GiftForm
