{-# LANGUAGE ForeignFunctionInterface #-}
-- We need this line to tell Haskell that we're
-- using the Foreign Function Interface (FFI) which
-- allows us to export functions to other languages
-- and similarly import them

{- |
 - To Compile: ghc -dynamic -shared -fPIC -lHSrts-ghc7.6.3 -o main.so main.hs
 
 - Let's break that down.
 - ghc is the haskell compiler
 - dynamic tells the compiler to
     use the shared versions of
     libraries, instead of the
     static ones.
 - shared tells the compiler to
     create a shared library
     instead of a program
 -fPIC tells the compiler that
     we want position independent
     code, helpful for being shared.
 -lHSrts-ghc7.6.3 specifies GHC RTS, 
     which needs to be specified
     explicitly for some reason.
     Also, if this doesn't work, 
     try to find your version.
 
 - for more info, check:
 - https://www.vex.net/~trebla/haskell/so.xhtml
 - https://downloads.haskell.org/~ghc/7.8.1/docs/html/users_guide/using-shared-libs.html
 -}
module TicTacToe where

import Foreign.C.Types
-- The modified types for use with C

import Foreign.Ptr
-- The module that handles C pointers

import Foreign.Marshal.Array
-- The module that allows for
-- reconstrucing lists from C pointers


-- Regular Haskell code


-- 0 represents an empty tile
-- 1 represents an X
-- 2 represents an O

-- Check for a win
check :: Int -> Int -> Int -> Bool
check a b c = a == b && a == c

checkWin' :: [Int] -> Int
checkWin' xs
    | checkRow1 = xs !! 0
    | checkRow2 = xs !! 3
    | checkRow3 = xs !! 6
    | checkCol1 = xs !! 0
    | checkCol2 = xs !! 1
    | checkCol3 = xs !! 2
    | checkDia1 = xs !! 0 
    | checkDia2 = xs !! 2
    | checkTie  = -1
    | otherwise = 0
    where
        (a:b:c:d:e:f:g:h:i:s) = xs
        checkRow1 = check a b c
        checkRow2 = check d e f
        checkRow3 = check g h i
        checkCol1 = check a d g
        checkCol2 = check b e h
        checkCol3 = check c f i
        checkDia1 = check a e i
        checkDia2 = check g e c
        checkTie  = not $ 0 `elem` xs

-- Check if a move is valid
checkValid' :: [Int] -> Int -> Int
checkValid' board elem
    | (board !! elem) == 0 = 1
    | otherwise            = 0


-- Now we redefine the pure haskell functions with C types.
-- Since the Pointer to the board is the only thing passed,
-- we need to wrap our output in an IO monad. 
-- Remember the pointer is, to oversimplify massively, just the first
-- element of the list. But we reconstruct the rest of
-- the list from it. Therefore, we could have the same pointer,
-- but a different list. The IO monad handles that uncertainty.

checkWin :: Ptr CInt -> IO CInt
checkWin boardPtr = do
    board <- peekArray 9 boardPtr
    -- peekArray reads the array, of length 9, starting at boardPtr.
    -- we bind the resulting list to board.

    (return . fromIntegral . checkWin') (map fromIntegral board)
    -- next, let's break down the ending statement.
    -- we have some function (return . fromIntegral . checkWin')
    -- and we're passing that function a list as an argument,
    -- that list is defined by (map fromIntegral board), which
    -- takes every CInt in board, and turns it into a Haskell Int.
    
    -- So now we have a function that's taking a standard haskell list
    -- of haskell ints as input. What is that function?
    -- return . fromIntegral . checkWin'
    -- checkWin' takes a list of Ints and returns an Int corresponding
    -- to the winner, if there is one.
    -- So we pass this output, a haskell Int, to fromIntegral, giving us
    -- back a CInt, and finally to return, which wraps it in an IO monad.
    
    -- alltoegether, we get a function that takes a pointer to a CInt array,
    -- and outputs an IO monad containing a CInt representing the gamestate.

checkValid :: Ptr CInt -> CInt -> IO CInt
checkValid boardPtr elem = do
    board <- peekArray 9 boardPtr
    -- once again, we read in the board from the pointer

    (return . fromIntegral) $ checkValid' (map fromIntegral board) (fromIntegral elem)
    -- now we check if a move is legal, namely that you can only play in a blank tile.
    -- we do this by checking if the index of the move in the board is 0 (empty).
    -- Let's break down this statement, now.

    -- We're going to call checkValid', which is definied in pure Haskell,
    -- and to do so, we need to convert our board and our index to regular Ints.
    -- So, we call checkValid' with fromIntegral mapped across board, and 
    -- fromIntegral on elem (our index).

    -- next, we push this checkValid' (a 1 or a 0 for a boolean value) through a
    -- function defined by fromIntegral and return. So, we convert our answer back
    -- into a CInt, and wrap it in an IO monad. 



-- Finally, we export as a C-Call checkWin and checkValid, alongside their type signatures.
foreign export ccall checkWin   :: Ptr CInt -> IO CInt
foreign export ccall checkValid :: Ptr CInt -> CInt -> IO CInt
