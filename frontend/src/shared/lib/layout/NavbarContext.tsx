import React, { createContext, useContext } from 'react';

type NavbarContextType = {
	isNavbarVisible: boolean;
	setNavbarVisible: React.Dispatch<React.SetStateAction<boolean>>;
	toggleNavbar: () => void;
};


export const NavbarContext = createContext<NavbarContextType | null>(null);

export const useNavbar = () => {
	const context = useContext(NavbarContext);

	if(!context) {
		throw new Error("useNavbar must be used inside NavbarContext.Provider");
	}

	return context;
}


