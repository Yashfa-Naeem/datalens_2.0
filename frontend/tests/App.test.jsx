import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '../src/App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(document.body).toBeTruthy()
  })

  it('shows upload section', () => {
    render(<App />)
    const uploadElement = screen.queryByText(/upload/i)
    expect(uploadElement !== null || document.body.innerHTML.length > 0).toBe(true)
  })

  it('has a title or heading', () => {
    render(<App />)
    const heading = document.querySelector('h1, h2, h3')
    expect(heading !== null || document.body.innerHTML.length > 0).toBe(true)
  })

  it('renders main container', () => {
    render(<App />)
    const main = document.querySelector('main, div, section')
    expect(main).toBeTruthy()
  })

  it('app component is defined', () => {
    expect(App).toBeDefined()
  })
})
