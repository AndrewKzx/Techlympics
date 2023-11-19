import { Fragment, useContext, useEffect, useRef, useState } from "react"
import { useRouter } from "next/router"
import { Event, getAllLocalStorageItems, getRefValue, getRefValues, isTrue, preventDefault, refs, set_val, spreadArraysOrObjects, uploadFiles, useEventLoop } from "/utils/state"
import { ColorModeContext, EventLoopContext, initialEvents, StateContext } from "/utils/context.js"
import "focus-visible/dist/focus-visible"
import { Box, Button, Center, Code, Container, Divider, Heading, HStack, Image, Input, Link, ListItem, Menu, MenuButton, MenuDivider, MenuItem, MenuList, Modal, ModalBody, ModalContent, ModalHeader, ModalOverlay, OrderedList, Spacer, Text, VStack } from "@chakra-ui/react"
import { getEventURL } from "/utils/state.js"
import NextLink from "next/link"
import { HamburgerIcon } from "@chakra-ui/icons"
import NextHead from "next/head"



export default function Component() {
  const state = useContext(StateContext)
  const router = useRouter()
  const [ colorMode, toggleColorMode ] = useContext(ColorModeContext)
  const focusRef = useRef();
  
  // Main event loop.
  const [addEvents, connectError] = useContext(EventLoopContext)

  // Set focus to the specified element.
  useEffect(() => {
    if (focusRef.current) {
      focusRef.current.focus();
    }
  })

  // Route after the initial page hydration.
  useEffect(() => {
    const change_complete = () => addEvents(initialEvents())
    router.events.on('routeChangeComplete', change_complete)
    return () => {
      router.events.off('routeChangeComplete', change_complete)
    }
  }, [router])

  const ref_installment = useRef(null); refs['ref_installment'] = ref_installment;
  const ref_loan = useRef(null); refs['ref_loan'] = ref_loan;
  const ref_expenses = useRef(null); refs['ref_expenses'] = ref_expenses;
  const ref_sym = useRef(null); refs['ref_sym'] = ref_sym;
  const ref_interest = useRef(null); refs['ref_interest'] = ref_interest;
  const ref_name = useRef(null); refs['ref_name'] = ref_name;
  const ref_income = useRef(null); refs['ref_income'] = ref_income;

  return (
    <Fragment>
  <Fragment>
  {isTrue(connectError !== null) ? (
  <Fragment>
  <Modal isOpen={connectError !== null}>
  <ModalOverlay>
  <ModalContent>
  <ModalHeader>
  {`Connection Error`}
</ModalHeader>
  <ModalBody>
  <Text>
  {`Cannot connect to server: `}
  {(connectError !== null) ? connectError.message : ''}
  {`. Check if server is reachable at `}
  {getEventURL().href}
</Text>
</ModalBody>
</ModalContent>
</ModalOverlay>
</Modal>
</Fragment>
) : (
  <Fragment/>
)}
</Fragment>
  <HStack alignItems={`flex-start`} sx={{"transition": "left 0.5s, width 0.5s", "position": "relative"}}>
  <Box sx={{"display": ["none", "none", "block"], "minWidth": "30em", "height": "100%", "position": "sticky", "overflowY": "auto", "top": "0px", "borderRight": "1px solid #F4F3F6"}}>
  <VStack sx={{"height": "100dvh"}}>
  <HStack sx={{"width": "400px", "borderBottom": "1px solid #F4F3F6", "padding": "1em"}}>
  <Text sx={{"backgroundImage": "linear-gradient(271.68deg, #4CAF50 0.75%, #81C784 88.52%)", "backgroundClip": "text", "fontWeight": "bold", "fontSize": "2em"}}>
  {`EconoMe`}
</Text>
  <Spacer/>
  <Link as={NextLink} href={`https://github.com/AndrewKzx/Techlympics`}>
  <Center sx={{"boxShadow": "0px 0px 0px 1px rgba(84, 82, 95, 0.14)", "bg": "transparent", "borderRadius": "0.375rem", "_hover": {"bg": "#F5EFFE"}}}>
  <Image src={`/github.svg`} sx={{"height": "3em", "padding": "0.5em"}}/>
</Center>
</Link>
  <Link as={NextLink} href={`https://data.gov.my/data-catalogue`}>
  <Center sx={{"boxShadow": "0px 0px 0px 1px rgba(84, 82, 95, 0.14)", "bg": "transparent", "borderRadius": "0.375rem", "_hover": {"bg": "#F5EFFE"}}}>
  <Image src={`/logo.webp`} sx={{"height": "3em", "padding": "0.5em"}}/>
</Center>
</Link>
</HStack>
  <VStack alignItems={`flex-start`} sx={{"width": "400px", "padding": "1em"}}>
  <Text className={`text-black-500 font-bold text-2xl`}>
  {`Loan Information`}
</Text>
  <Container sx={{"padding": "1rem", "border": "1px solid #F4F3F6", "borderRadius": "0.375rem", "boxShadow": "0px 0px 0px 1px rgba(84, 82, 95, 0.14)"}}>
  <OrderedList>
  <Container sx={{"borderRadius": "0.375rem", "boxShadow": "0px 0px 0px 1px rgba(84, 82, 95, 0.14)", "width": "100%"}}>
  {state.show_loans.map((effzvbne, i) => (
  <ListItem key={i}>
  <HStack>
  <Box dangerouslySetInnerHTML={{"__html": effzvbne}}/>
  <Button onClick={(_e) => addEvents([Event("state.finish_item", {item:effzvbne})], (_e))} sx={{"height": "1.5em", "backgroundColor": "white", "textColor": "white", "fontSize": "1em"}}>
  {`❌`}
</Button>
</HStack>
</ListItem>
))}
</Container>
</OrderedList>
  <Box as={`form`} onSubmit={(_e0) => addEvents([Event("state.add_item", {form_data:{"interest": getRefValue(ref_interest), "sym": getRefValue(ref_sym), "installment": getRefValue(ref_installment), "name": getRefValue(ref_name), "loan": getRefValue(ref_loan)}})], (_e0))}>
  <Text className={`text-black-500 font-bold mb-2`}>
  {`Starting Date Info`}
</Text>
  <Input className={`mb-4`} id={`sym`} placeholder={`Enter Starting Year and Month (2023/05)`} ref={ref_sym} type={`text`}/>
  <Text className={`text-black-500 font-bold mb-2`}>
  {`Relevant Loan Info`}
</Text>
  <Input className={`mb-4`} id={`name`} placeholder={`Enter Loan Name`} ref={ref_name} type={`text`}/>
  <Input className={`mb-4`} id={`loan`} placeholder={`Enter Loan Amount (RM)`} ref={ref_loan} type={`text`}/>
  <Input className={`mb-4`} id={`interest`} placeholder={`Enter Interest Rate (%)`} ref={ref_interest} type={`text`}/>
  <Input id={`installment`} placeholder={`Installment (Months)`} ref={ref_installment} type={`text`}/>
  <Center>
  <Button sx={{"bg": "green", "color": "white", "marginTop": "1rem"}} type={`submit`}>
  {`Add`}
</Button>
</Center>
</Box>
</Container>
  <Box as={`form`} onSubmit={(_e0) => addEvents([Event("state.handle_submit", {form_data:{"income": getRefValue(ref_income), "expenses": getRefValue(ref_expenses)}})], (_e0))}>
  <Text className={`text-black-500 font-bold text-2xl mt-4 mb-2`}>
  {`Financial Information`}
</Text>
  <Container sx={{"padding": "1rem", "maxWidth": "400px", "border": "1px solid #F4F3F6", "borderRadius": "0.375rem", "boxShadow": "0px 0px 0px 1px rgba(84, 82, 95, 0.14)"}}>
  <Text className={`text-black-500 font-bold mb-2`}>
  {`Household Income`}
</Text>
  <Input id={`income`} placeholder={`Enter Current Household Income`} ref={ref_income} type={`text`}/>
  <Text className={`text-black-500 font-bold mb-2 mt-4`}>
  {`Monthly Expenses (Not inclusive of loan(s))`}
</Text>
  <Input id={`expenses`} placeholder={`Enter Usual Monthly Expenses`} ref={ref_expenses} type={`text`}/>
  <Center>
  <Button className={`bg-blue-500 text-white mt-3`} sx={{"bg": "green"}} type={`submit`}>
  {`Generate`}
</Button>
</Center>
</Container>
</Box>
  <Spacer/>
  <Divider/>
</VStack>
  <Spacer/>
  <HStack sx={{"width": "100%", "borderTop": "1px solid #F4F3F6", "padding": "1em"}}>
  <Spacer/>
  <Link as={NextLink} href={`https://reflex.dev/docs/getting-started/introduction/`}>
  <Text>
  {`Docs`}
</Text>
</Link>
  <Link as={NextLink} href={`https://reflex.dev/blog/`}>
  <Text>
  {`Blog`}
</Text>
</Link>
</HStack>
</VStack>
</Box>
  <Box sx={{"paddingTop": "5em", "paddingX": ["auto", "2em"]}}>
  <Box sx={{"width": "800px", "alignItems": "flex-center", "padding": "1em", "marginBottom": "2em"}}>
  <VStack>
  <Heading sx={{"fontSize": "3em"}}>
  {`Settings`}
</Heading>
  <Text>
  {`Welcome to Reflex!`}
</Text>
  <Text>
  {`You can edit this page in `}
  <Code>
  {`{your_app}/pages/settings.py`}
</Code>
</Text>
</VStack>
</Box>
</Box>
  <Spacer/>
  <Box sx={{"position": "fixed", "right": "1.5em", "top": "1.5em", "zIndex": "500"}}>
  <Menu>
  <MenuButton sx={{"width": "3em", "height": "3em", "backgroundColor": "white"}}>
  <HamburgerIcon sx={{"size": "4em", "color": "black"}}/>
</MenuButton>
  <MenuList>
  <MenuItem sx={{"_hover": {"bg": "#F5EFFE"}}}>
  <Link as={NextLink} href={`/`} sx={{"width": "100%"}}>
  {`Home`}
</Link>
</MenuItem>
  <MenuItem sx={{"_hover": {"bg": "#F5EFFE"}}}>
  <Link as={NextLink} href={`/dashboard`} sx={{"width": "100%"}}>
  {`Dashboard`}
</Link>
</MenuItem>
  <MenuItem sx={{"_hover": {"bg": "#F5EFFE"}}}>
  <Link as={NextLink} href={`/settings`} sx={{"width": "100%"}}>
  {`Settings`}
</Link>
</MenuItem>
  <MenuDivider/>
  <MenuItem sx={{"_hover": {"bg": "#F5EFFE"}}}>
  <Link as={NextLink} href={`https://github.com/reflex-dev`} sx={{"width": "100%"}}>
  {`About`}
</Link>
</MenuItem>
  <MenuItem sx={{"_hover": {"bg": "#F5EFFE"}}}>
  <Link as={NextLink} href={`mailto:founders@=reflex.dev`} sx={{"width": "100%"}}>
  {`Contact`}
</Link>
</MenuItem>
</MenuList>
</Menu>
</Box>
</HStack>
  <NextHead>
  <title>
  {`Settings`}
</title>
  <meta content={`A Reflex app.`} name={`description`}/>
  <meta content={`favicon.ico`} property={`og:image`}/>
  <meta content={`width=device-width, shrink-to-fit=no, initial-scale=1`} name={`viewport`}/>
</NextHead>
</Fragment>
  )
}
