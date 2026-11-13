"use client"

import { useActionState } from "react"

import {
  createListingAction,
  type ListingFormState,
} from "@/app/(tabs)/create/[kind]/actions"
import { FormField } from "@/components/serve/form-field"
import { PhotoPicker } from "@/components/serve/photo-picker"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { NativeSelect } from "@/components/ui/native-select"
import { Textarea } from "@/components/ui/textarea"
import {
  conditionNames,
  itemCategoryNames,
  serviceCategoryNames,
} from "@/lib/categories"
import type { ShopRef } from "@/lib/types"

const initial: ListingFormState = {}

/** The form for "Sell an item" and "Offer a service". They differ in two fields. */
export function ListingForm({
  kind,
  shop,
}: {
  kind: "sell-item" | "offer-service"
  shop: ShopRef | null
}) {
  const isItem = kind === "sell-item"
  const [state, formAction, pending] = useActionState(
    createListingAction.bind(null, kind),
    initial
  )
  const errors = state.fieldErrors ?? {}
  const v = state.values ?? {}
  const categories = Object.entries(
    isItem ? itemCategoryNames : serviceCategoryNames
  )

  return (
    <form
      action={formAction}
      className="flex max-w-2xl flex-col gap-5 rounded-2xl bg-card p-5 ring-1 ring-foreground/5 md:p-8"
    >
      <PhotoPicker uploaded={state.photo} error={errors.photo} />

      <FormField label="Title" error={errors.title}>
        <Input
          name="title"
          required
          maxLength={200}
          defaultValue={v.title}
          placeholder={
            isItem ? "e.g. Casio FX-570EX calculator" : "e.g. Haircut at KTDI"
          }
          className="h-11 rounded-xl"
        />
      </FormField>

      <div className="grid gap-5 sm:grid-cols-2">
        <FormField label="Category" error={errors.category}>
          <NativeSelect name="category" required defaultValue={v.category ?? ""}>
            <option value="" disabled>
              Choose one
            </option>
            {categories.map(([value, name]) => (
              <option key={value} value={value}>
                {name}
              </option>
            ))}
          </NativeSelect>
        </FormField>

        {isItem && (
          <FormField label="Condition" error={errors.condition}>
            <NativeSelect
              name="condition"
              required
              defaultValue={v.condition ?? ""}
            >
              <option value="" disabled>
                Choose one
              </option>
              {Object.entries(conditionNames).map(([value, name]) => (
                <option key={value} value={value}>
                  {name}
                </option>
              ))}
            </NativeSelect>
          </FormField>
        )}
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <FormField label="Price (RM)" error={errors.price}>
          <Input
            name="price"
            type="number"
            inputMode="decimal"
            required
            min="0.01"
            max="99999.99"
            step="0.01"
            defaultValue={v.price}
            className="h-11 rounded-xl"
          />
        </FormField>

        {!isItem && (
          <FormField
            label="Per"
            optional
            hint="What the price covers, like hour or page. Leave blank for a flat price."
            error={errors.unit}
          >
            <Input
              name="unit"
              maxLength={30}
              defaultValue={v.unit}
              placeholder="hour"
              className="h-11 rounded-xl"
            />
          </FormField>
        )}
      </div>

      <FormField
        label="Description"
        optional
        hint={
          isItem
            ? "Anything a buyer should know: edition, flaws, why you're selling."
            : "What you offer, how long it takes, what to bring."
        }
        error={errors.description}
      >
        <Textarea
          name="description"
          maxLength={5000}
          defaultValue={v.description}
          className="rounded-xl"
        />
      </FormField>

      <FormField
        label={isItem ? "Meetup spot" : "Where it happens"}
        hint={
          isItem
            ? "Where on campus you can hand it over, like PSZ lobby or KTDI cafe."
            : "Where on campus students find you."
        }
        error={errors.spot}
      >
        <Input
          name="spot"
          required
          maxLength={200}
          defaultValue={v.spot}
          className="h-11 rounded-xl"
        />
      </FormField>

      {shop && (
        <label className="flex items-start gap-3 text-sm">
          <input
            type="checkbox"
            name="useShop"
            defaultChecked={v.useShop === "on"}
            className="mt-0.5 size-4 accent-primary"
          />
          <span>
            <span className="font-medium">List under {shop.name}</span>
            <span className="block text-muted-foreground">
              It will also appear on your shop page.
            </span>
          </span>
        </label>
      )}

      {state.message && (
        <p role="alert" className="text-sm text-destructive">
          {state.message}
        </p>
      )}

      <Button type="submit" disabled={pending} className="h-11 rounded-xl px-6 sm:self-start">
        {pending ? "Publishing…" : "Publish"}
      </Button>
    </form>
  )
}
