import * as yup from 'yup'

export const emailValidation = (t) =>
  yup
    .string()
    .required(t('validation.emailRequired'))
    .email(t('validation.emailInvalid'))
    .matches(/@.+\./, t('validation.emailInvalid'))

export const passwordValidation = (t, min = 4) =>
  yup
    .string()
    .required(t('validation.passwordRequired'))
    .min(min, t('validation.passwordMin', { min }))
