import { useFormik } from "formik"
import { ReactElement, useEffect } from "react"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
import * as Yup from "yup"

import Button from "@mui/material/Button"
import Card from "@mui/material/Card"
import CardActions from "@mui/material/CardActions"
import CardContent from "@mui/material/CardContent"
import TextField from "@mui/material/TextField"
import Typography from "@mui/material/Typography"

import styles from "./style.module.scss"

interface LoginFormValues {
  username: string
  password: string
}

const validationSchema = Yup.object({
  username: Yup.string().email().required(),
  password: Yup.string().required(),
})

function LoginComponent({ args }: ComponentProps): ReactElement {
  const { title } = args

  useEffect(() => {
    Streamlit.setFrameHeight()
  })

  const formik = useFormik<LoginFormValues>({
    initialValues: {
      username: "",
      password: "",
    },
    validationSchema: validationSchema,
    onSubmit: (values, { setSubmitting }) => {
      setSubmitting(false)
      Streamlit.setComponentValue(values)
    },
    onReset: () => {
      Streamlit.setComponentValue({})
    },
  })

  return (
    <form
      onSubmit={formik.handleSubmit}
      onReset={formik.handleReset}
      className={styles.loginForm}
    >
      <Card>
        <CardContent>
          <Typography gutterBottom variant="h5" component="h2">
            {title}
          </Typography>

          <TextField
            id="username"
            name="username"
            label="Username"
            placeholder="username@domain.com"
            value={formik.values.username}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.username && Boolean(formik.errors.username)}
            helperText={formik.touched.username && formik.errors.username}
            fullWidth
            margin="dense"
          />

          <TextField
            id="password"
            name="password"
            label="Password"
            type="password"
            placeholder="your password"
            value={formik.values.password}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.password && Boolean(formik.errors.password)}
            helperText={formik.touched.password && formik.errors.password}
            fullWidth
            margin="dense"
          />
        </CardContent>
        <CardActions>
          <Button
            type="submit"
            color="primary"
            disabled={formik.isSubmitting || !formik.isValid}
          >
            Login
          </Button>
          <Button type="reset" color="secondary">
            Cancel
          </Button>
        </CardActions>
      </Card>
    </form>
  )
}

export default withStreamlitConnection(LoginComponent)
