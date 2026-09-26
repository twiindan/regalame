/*
ABOUTME: Form component for creating gifts.
ABOUTME: Uploads the optional image first, then creates the gift as JSON.
*/

import { Button, Input, Textarea, VStack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import { GiftsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { Field } from "../ui/field"

interface GiftFormValues {
  name: string
  approximate_price: number
  description?: string
  product_link?: string
  photo?: FileList
}

const GiftForm = () => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<GiftFormValues>({
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
    mutationFn: async (data: GiftFormValues) => {
      // Creation is JSON and the image travels in its own multipart request, so
      // upload the picture first and reference the URL it returns.
      let photoUrl: string | null = null
      const file = data.photo?.[0]
      if (file) {
        const uploaded = await GiftsService.uploadGiftImage({
          formData: { file },
        })
        photoUrl = uploaded.photo_url
      }

      return GiftsService.createGift({
        requestBody: {
          name: data.name,
          approximate_price: data.approximate_price,
          description: data.description || null,
          product_link: data.product_link || null,
          photo_url: photoUrl,
        },
      })
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

  const onSubmit: SubmitHandler<GiftFormValues> = (data) => {
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
