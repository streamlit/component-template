import React, {useEffect, ReactElement} from "react"
import {
  withStreamlitConnection,
  Streamlit,
  ComponentProps,
} from "streamlit-component-lib"
import * as Yup from 'yup'
import {Formik, Form, Field} from 'formik'

import Card from '@material-ui/core/Card'
import Button from '@material-ui/core/Button'
import TextField from '@material-ui/core/TextField'
import Typography from '@material-ui/core/Typography'
import CardActions from '@material-ui/core/CardActions'
import CardContent from '@material-ui/core/CardContent'

import styles from './style.module.scss'

function LoginComponent({args}: ComponentProps): ReactElement {
  const {title} = args

  const initialValues = {
    username: '',
    password: '',
  }
  const validationSchema = Yup.object({
    username: Yup.string().email().required(),
    password: Yup.string().required(),
  })

  useEffect(() => {
    Streamlit.setFrameHeight()
  })

  const onSubmit = (values: any, {setSubmitting}: any) => {
    setSubmitting(false)
    Streamlit.setComponentValue(values)
  }

  const onReset = () => Streamlit.setComponentValue({})

  return (
    <Formik initialValues={initialValues} validationSchema={validationSchema} onSubmit={onSubmit} onReset={onReset}>
      {({errors, isSubmitting}: any) => (
        <Form className={styles.loginForm}>
          <Card>
            <CardContent>
              <Typography gutterBottom variant="h5" component="h2">
                {title}
              </Typography>

              <Field
                name="username"
                placeholder="username@domain.com"
                as={TextField}
                fullWidth
                margin="dense"
                error={Boolean(errors.username)}
                helperText={errors.username}
              />

              <Field
                type="password"
                name="password"
                placeholder="your password"
                as={TextField}
                fullWidth
                margin="dense"
                error={Boolean(errors.password)}
                helperText={errors.password}
              />
            </CardContent>
            <CardActions>
              <Button
                type="submit"
                color="primary"
                disabled={isSubmitting || Object.keys(errors).length > 0}
              >
                Login
              </Button>
              <Button type="reset" color="secondary">
                Cancel
              </Button>
            </CardActions>
          </Card>
        </Form>
      )}
    </Formik>
  )
}

export default withStreamlitConnection(LoginComponent)
